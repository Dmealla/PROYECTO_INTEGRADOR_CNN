import argparse
import cv2
import db
import rostro


def main(nombre, contacto, n=40):
    db.init()
    cid = db.agregar_conductor(nombre, contacto)
    cam = cv2.VideoCapture(0)
    cont = 0
    while cont < n:
        ok, frame = cam.read()
        if not ok:
            break
        r = rostro.detectar_rostro(frame)
        if r:
            x, y, w, h = r
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            db.guardar_rostro(cid, cv2.resize(gray[y:y + h, x:x + w], (db.TAM, db.TAM)))
            cont += 1
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"{cont}/{n}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Cargar conductor - q para salir", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cam.release()
    cv2.destroyAllWindows()
    print(f"Conductor '{nombre}' guardado con {cont} rostros.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--contacto", default="")
    a = ap.parse_args()
    main(a.nombre.strip().lower(), a.contacto.strip())
