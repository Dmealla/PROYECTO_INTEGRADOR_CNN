# Sistema de Identificación de Conductor y Detección de Somnolencia

Proyecto Integrador de Diego Sebastián Mealla y Horacio Barrabasqui.

Identifica al conductor con la cámara web, detecta somnolencia en tiempo real y da
alertas por voz, por Arduino (opcional) y por Telegram (opcional).

## Requisitos

- **Windows 10 u 11**
- **Python 3.12** (MediaPipe 0.10.14 no funciona con versiones más nuevas)
- Cámara web

## Instalación

```powershell
git clone https://github.com/Dmealla/PROYECTO_INTEGRADOR_CNN.git
cd PROYECTO_INTEGRADOR_CNN
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Uso

1. **Registrar un conductor:** abrir `gestor.bat` y cargar el nombre. La cámara toma las fotos del rostro.
2. **Iniciar el sistema:** abrir `sistema.bat`. Identifica al conductor y empieza a controlar la somnolencia.
3. **Salir:** tecla `q`.

## Telegram (opcional)

Sin esta configuración el sistema funciona igual, pero no envía mensajes.

1. Pedir el token del bot al responsable del proyecto **por un medio privado**.
2. Guardarlo como variable de entorno y **abrir una terminal nueva**:

```powershell
setx TG_TOKEN "PEGAR_EL_TOKEN_ACA"
```

El token nunca se escribe en el código ni se sube a GitHub.

## Arduino (opcional)

Cargar `arduino/deteccion_rostro/deteccion_rostro.ino` en la placa. Sin Arduino conectado,
el sistema funciona con alertas por voz y en pantalla.

## CNN de ojos (opcional)

Sin el modelo `cnn/ojos.onnx`, el sistema detecta los ojos cerrados con EAR (Eye Aspect Ratio).

**Capturar imágenes de una sesión** (`s1`, `s2`, etc.; teclas `a`, `c`, `s` y `q`):

```powershell
.\.venv\Scripts\python.exe cnn\capturar_ojos.py s1
```

**Instalar el entorno de entrenamiento** (va separado porque TensorFlow y MediaPipe
necesitan versiones distintas de `protobuf`):

```powershell
py -3.12 -m venv .venv-rostros
.\.venv-rostros\Scripts\python.exe -m pip install -r requirements-entrenamiento.txt
```

## Privacidad

`conductores.db` y `cnn/dataset/` contienen datos biométricos y **no se suben a GitHub**.
Cada persona registra sus propios datos en su PC.