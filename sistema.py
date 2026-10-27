import os
import time
import threading
import urllib.parse
import urllib.request
import cv2
import numpy as np
import mediapipe as mp
import pyttsx3
import db
import config
import rostro

TTS = pyttsx3.init()
OJO_I = [33, 160, 158, 133, 153, 144]
OJO_D = [362, 385, 387, 263, 373, 380]

MP_DRAW = mp.solutions.drawing_utils
MP_STYLES = mp.solutions.drawing_styles
FACEMESH = mp.solutions.face_mesh

CNN = cv2.dnn.readNetFromONNX("cnn/ojos.onnx") if os.path.exists("cnn/ojos.onnx") else None


def _recorte_ojo(gray, pts, idx, m=0.6):
    xs, ys = pts[idx, 0], pts[idx, 1]
    x1, x2, y1, y2 = xs.min(), xs.max(), ys.min(), ys.max()
    w, h = x2 - x1, y2 - y1
    x1, x2 = int(max(0, x1 - w * m)), int(x2 + w * m)
    y1, y2 = int(max(0, y1 - h * m)), int(y2 + h * m)
    c = gray[y1:y2, x1:x2]
    if c.size == 0:
        return None
    return cv2.resize(c, (24, 24))


def prob_cerrado(gray, pts):
    probs = []
    for idx in (OJO_I, OJO_D):
        c = _recorte_ojo(gray, pts, idx)
        if c is None:
            continue
        blob = (c.astype("float32") / 255.0).reshape(1, 24, 24, 1)
        CNN.setInput(blob)
        probs.append(float(CNN.forward().ravel()[0]))
    return sum(probs) / len(probs) if probs else None

try:
    import serial
    import serial.tools.list_ports as _lp
    _SERIAL = True
except Exception:
    _SERIAL = False


def abrir_arduino():
    if not _SERIAL:
        return None
    try:
        puertos = list(_lp.comports())
        dev = None
        for p in puertos:
            d = (p.description + " " + (p.manufacturer or "")).lower()
            if any(k in d for k in ["ch340", "ch341", "arduino", "usb-serial", "usb serial"]):
                dev = p.device
                break
        if not dev and len(puertos) == 1:
            dev = puertos[0].device
        if not dev:
            print("Sin Arduino conectado.")
            return None
        s = serial.Serial(dev, 9600, timeout=1)
        time.sleep(2)
        print("Arduino conectado en", dev)
        return s
    except Exception as e:
        print("Sin Arduino:", e)
        return None


def hablar(texto):
    threading.Thread(target=lambda: (TTS.say(texto), TTS.runAndWait()), daemon=True).start()


def telegram(chat, texto):
    if not config.TG_TOKEN or not chat:
        return
    url = "https://api.telegram.org/bot%s/sendMessage?%s" % (
        config.TG_TOKEN, urllib.parse.urlencode({"chat_id": chat, "text": texto}))
    try:
        urllib.request.urlopen(url, timeout=10)
    except Exception:
        pass


def ear(p):
    v = np.linalg.norm(p[1] - p[5]) + np.linalg.norm(p[2] - p[4])
    h = 2 * np.linalg.norm(p[0] - p[3])
    return v / (h + 1e-8)


def contar_estable(elegido, estable, id_):
    if id_ == elegido:
        estable += 1
    else:
        elegido = id_
        estable = 1
    return elegido, estable



def identificar():
    caras, labels, nombres = db.datos_entrenamiento()
    if not caras:
        print("No hay conductores. Ejecuta cargar_conductor.py primero.")
        return None, ""
    reco = cv2.face.LBPHFaceRecognizer_create()
    reco.train(caras, np.array(labels))
    cam = cv2.VideoCapture(0)
    elegido, nombre, estable = None, "", 0
    t0 = time.time()
    while time.time() - t0 < 30:
        ok, frame = cam.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        r = rostro.detectar_rostro(frame)
        if r:
            x, y, w, h = r
            id_, conf = reco.predict(cv2.resize(gray[y:y + h, x:x + w], (db.TAM, db.TAM)))
            if conf < config.UMBRAL_ROSTRO:
                elegido, estable = contar_estable(elegido, estable, id_)
                nombre = nombres.get(id_, "?")
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, nombre, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                estable = 0
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "Desconocido", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            estable = 0
        cv2.putText(frame, "Identificando conductor...", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("Sistema - q para salir", frame)
        if estable >= config.FRAMES_CONFIRMAR:
            cam.release()
            return elegido, nombre
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cam.release()
    return None, ""


def somnolencia(nombre, chat):
    malla = mp.solutions.face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True,
                                            min_detection_confidence=0.5, min_tracking_confidence=0.5)
    cam = cv2.VideoCapture(0)
    ard = abrir_arduino()
    cerrado, alarma, micros, ultimo = None, False, 0, 0
    sin_rostro = None
    hablar("Bienvenido " + nombre)
    while True:
        ok, frame = cam.read()
        if not ok:
            break
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        res = malla.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        estado, color = "Sin rostro", (150, 150, 150)
        if res.multi_face_landmarks:
            sin_rostro = None
            face = res.multi_face_landmarks[0]
            lm = face.landmark
            pts = np.array([(p.x * w, p.y * h) for p in lm])
            if config.MOSTRAR_MALLA:
                MP_DRAW.draw_landmarks(frame, face, FACEMESH.FACEMESH_TESSELATION, None,
                                       MP_STYLES.get_default_face_mesh_tesselation_style())
                MP_DRAW.draw_landmarks(frame, face, FACEMESH.FACEMESH_CONTOURS, None,
                                       MP_STYLES.get_default_face_mesh_contours_style())
            if CNN is not None:
                pc = prob_cerrado(gray, pts)
                cerrado_ojo = pc is not None and pc > 0.5
            else:
                cerrado_ojo = (ear(pts[OJO_I]) + ear(pts[OJO_D])) / 2 < config.EAR_UMBRAL
            if cerrado_ojo:
                cerrado = cerrado or time.time()
                if time.time() - cerrado >= config.SEG_ALERTA:
                    estado, color = "DESPIERTA!", (0, 0, 255)
                    if not alarma:
                        alarma = True
                        micros += 1
                        hablar("Despierta")
                        if ard:
                            ard.write(b"B")
                        if micros % config.MICROSUENOS_ALERTA == 0 and time.time() - ultimo > config.COOLDOWN:
                            ultimo = time.time()
                            msg = "ALERTA de somnolencia: %s. Microsuenos: %d. Hora: %s" % (
                                nombre, micros, time.strftime("%H:%M"))
                            threading.Thread(target=telegram, args=(chat, msg)).start()
                else:
                    estado, color = "Ojos cerrados...", (0, 165, 255)
            else:
                if alarma and ard:
                    ard.write(b"b")
                cerrado, alarma = None, False
                estado, color = "Despierto", (0, 255, 0)
        else:
            sin_rostro = sin_rostro or time.time()
            if time.time() - sin_rostro >= config.SEG_SIN_ROSTRO:
                estado, color = "MIRE AL FRENTE!", (0, 0, 255)
                if not alarma:
                    alarma = True
                    hablar("Mire al frente")
                    if ard:
                        ard.write(b"B")
        cv2.putText(frame, estado, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, "Conductor: " + nombre, (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.imshow("Sistema - q para salir", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cam.release()
    cv2.destroyAllWindows()
    malla.close()
    if ard:
        ard.write(b"X")
        ard.close()


def main():
    db.init()
    cid, nombre = identificar()
    cv2.destroyAllWindows()
    if not cid:
        print("No se identifico ningun conductor.")
        return
    somnolencia(nombre, db.chat_id(cid))


if __name__ == "__main__":
    main()
