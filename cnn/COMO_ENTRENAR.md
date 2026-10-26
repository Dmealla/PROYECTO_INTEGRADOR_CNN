# CNN propia: clasificador de ojos abiertos/cerrados

Esta CNN la entrenás vos con tus propias imágenes. Detecta si los ojos están
abiertos o cerrados y reemplaza al EAR en la detección de somnolencia (el EAR
queda como respaldo si todavía no entrenaste la CNN).

Flujo: **capturar imágenes → entrenar → exportar a ONNX → el sistema la usa sola.**

## 1. Capturar el dataset (entorno .venv)

```bash
F:\Desktop\.venv\Scripts\python.exe cnn\capturar_ojos.py
```

Se abre la cámara. Teclas:
- **a** → empieza a guardar imágenes de **ojos ABIERTOS** (mirá normal, parpadeá poco).
- **c** → empieza a guardar **ojos CERRADOS** (cerrá los ojos).
- **s** → parar de guardar.
- **q** → salir.

Juntá al menos **200 de cada** (cuantas más y más variadas —luz, ángulo—, mejor).
Las imágenes quedan en `cnn/dataset/abiertos/` y `cnn/dataset/cerrados/`.

## 2. Entrenar la CNN (entorno .venv-rostros)

```bash
F:\Desktop\prueba\.venv-rostros\Scripts\python.exe cnn\entrenar_ojos.py
```

Entrena la red y **exporta el modelo a `cnn/ojos.onnx`**. Mirá el `accuracy` y
`val_accuracy` al final: si ambos son altos (>0.9), quedó bien.

## 3. Usarla

No hay que hacer nada más: al iniciar `sistema.py`, si existe `cnn/ojos.onnx`
lo carga automáticamente con OpenCV (cv2.dnn) y detecta la somnolencia con la
**CNN** en vez del EAR.

```bash
sistema.bat
```

## Arquitectura de la CNN

Entrada 24×24 en escala de grises → `Conv(16) + MaxPool` → `Conv(32) + MaxPool`
→ `Flatten` → `Dense(64)` → `Dropout(0.4)` → `Dense(1, sigmoid)`.
Salida: probabilidad de "ojo cerrado" (umbral 0.5).

## Nota técnica (para la defensa)

- La CNN se **entrena en Keras/TensorFlow** y se **exporta a ONNX**.
- En ejecución se corre con **OpenCV (cv2.dnn)**, que no necesita TensorFlow,
  por eso convive con MediaPipe en un mismo programa (evita el conflicto de
  protobuf entre TensorFlow y MediaPipe).
- Dependencias de entrenamiento (ya instaladas en .venv-rostros): `tf2onnx`, `onnx`.
