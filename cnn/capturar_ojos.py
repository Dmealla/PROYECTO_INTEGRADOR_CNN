import os
import cv2
import numpy as np
import mediapipe as mp

OJO_I = [33, 160, 158, 133, 153, 144]
OJO_D = [362, 385, 387, 263, 373, 380]
DIR = "cnn/dataset"


def recorte(gray, pts, idx, m=0.6):
    xs, ys = pts[idx, 0], pts[idx, 1]
    x1, x2, y1, y2 = xs.min(), xs.max(), ys.min(), ys.max()
    w, h = x2 - x1, y2 - y1
    x1, x2 = int(max(0, x1 - w * m)), int(x2 + w * m)
    y1, y2 = int(max(0, y1 - h * m)), int(y2 + h * m)
    c = gray[y1:y2, x1:x2]
    if c.size == 0:
        return None
    return cv2.resize(c, (24, 24))


def main():
    for t in ("abiertos", "cerrados"):
        os.makedirs(f"{DIR}/{t}", exist_ok=True)
    cont = {t: len(os.listdir(f"{DIR}/{t}")) for t in ("abiertos", "cerrados")}
    malla = mp.solutions.face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True,
                                            min_detection_confidence=0.5, min_tracking_confidence=0.5)
    cam = cv2.VideoCapture(0)
    modo = None
    print("a = guardar ABIERTOS   c = guardar CERRADOS   s = parar   q = salir")
    while True:
        ok, frame = cam.read()
        if not ok:
            break
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        res = malla.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if res.multi_face_landmarks and modo:
            lm = res.multi_face_landmarks[0].landmark
            pts = np.array([(p.x * w, p.y * h) for p in lm])
            for idx in (OJO_I, OJO_D):
                c = recorte(gray, pts, idx)
                if c is not None:
                    cv2.imwrite(f"{DIR}/{modo}/{cont[modo]}.png", c)
                    cont[modo] += 1
        cv2.putText(frame, f"modo:{modo}  abiertos:{cont['abiertos']}  cerrados:{cont['cerrados']}",
                    (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Capturar ojos - a/c/s/q", frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord("a"):
            modo = "abiertos"
        elif k == ord("c"):
            modo = "cerrados"
        elif k == ord("s"):
            modo = None
        elif k == ord("q"):
            break
    cam.release()
    cv2.destroyAllWindows()
    print("Guardado:", cont)


if __name__ == "__main__":
    main()
