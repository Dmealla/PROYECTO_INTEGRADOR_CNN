import os
import cv2
import numpy as np
import tensorflow as tf
import tf_keras as keras
import tf2onnx

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ojos.onnx")


def cargar(sesiones):
    X, Y = [], []
    for s in sesiones:
        for label, t in enumerate(("abiertos", "cerrados")):
            d = f"{DIR}/{s}/{t}"
            if not os.path.isdir(d):
                continue
            for f in os.listdir(d):
                img = cv2.imread(os.path.join(d, f), cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                X.append(cv2.resize(img, (24, 24)))
                Y.append(label)
    X = np.array(X, dtype="float32").reshape(-1, 24, 24, 1) / 255.0
    Y = np.array(Y, dtype="float32")
    return X, Y


def main():
    X, Y = cargar()
    print(f"Muestras: {len(X)}  (abiertos={(Y == 0).sum()}, cerrados={(Y == 1).sum()})")
    if len(X) < 20:
        print("Pocas muestras. Captura mas con capturar_ojos.py")
        return
    m = keras.Sequential([
        keras.layers.Input((24, 24, 1)),
        keras.layers.Conv2D(16, 3, activation="relu"),
        keras.layers.MaxPooling2D(),
        keras.layers.Conv2D(32, 3, activation="relu"),
        keras.layers.MaxPooling2D(),
        keras.layers.Flatten(),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dropout(0.4),
        keras.layers.Dense(1, activation="sigmoid"),
    ])
    m.compile("adam", "binary_crossentropy", metrics=["accuracy"])
    m.fit(X, Y, epochs=15, batch_size=32, validation_split=0.2)
    spec = (tf.TensorSpec((None, 24, 24, 1), tf.float32, name="input"),)
    tf2onnx.convert.from_keras(m, input_signature=spec, opset=13, output_path=SALIDA)
    print("Modelo CNN exportado en", SALIDA)


if __name__ == "__main__":
    main()
