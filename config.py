import os

# El token de Telegram se lee de la variable de entorno TG_TOKEN (no se guarda en el código)
TG_TOKEN = os.environ.get("TG_TOKEN", "")

UMBRAL_ROSTRO = 70
FRAMES_CONFIRMAR = 15

EAR_UMBRAL = 0.21
SEG_ALERTA = 1.2
MICROSUENOS_ALERTA = 3
COOLDOWN = 120
SEG_SIN_ROSTRO = 2.0

MOSTRAR_MALLA = True
