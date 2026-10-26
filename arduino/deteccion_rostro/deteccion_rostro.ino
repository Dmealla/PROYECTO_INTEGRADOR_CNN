/*
  Recibe una letra por el puerto serie:
    'D' -> LED de Diego  (pin 8)
    'F' -> LED de Franco (pin 9)
    'B' -> buzzer SONANDO (pin 7)   -> alarma (ej. somnolencia)
    'b' -> buzzer APAGADO
    'X' -> apaga todo
  El PC (Python) envia estas letras.

  Cableado:
    - LEDs: cada uno con resistencia de 220 ohm al pin, otro extremo a GND.
    - Buzzer: pata (+) al pin 7, pata (-) a GND.
  Este codigo asume BUZZER ACTIVO (suena con HIGH). Si es PASIVO, mira el
  comentario en el case 'B'.
*/

const int LED_DIEGO  = 8;
const int LED_FRANCO = 9;
const int BUZZER     = 7;
const int LED_ALARMA = 6;   // LED que DESTELLA en la alarma

// Estado del destello (parpadeo sin bloquear con millis)
bool alarma = false;
bool destelloEncendido = false;
unsigned long ultimoCambio = 0;
const unsigned long INTERVALO = 100;   // ms entre destellos (mas bajo = mas rapido)

void setup() {
  pinMode(LED_DIEGO, OUTPUT);
  pinMode(LED_FRANCO, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  pinMode(LED_ALARMA, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    switch (c) {
      case 'D':
        digitalWrite(LED_DIEGO, HIGH);
        Serial.println("OK: LED Diego ENCENDIDO");
        break;
      case 'F':
        digitalWrite(LED_FRANCO, HIGH);
        Serial.println("OK: LED Franco ENCENDIDO");
        break;
      case 'B':
        alarma = true;                   // arranca el destello
        tone(BUZZER, 1200);              // BUZZER PASIVO: suena a 1200 Hz
        Serial.println("OK: ALARMA (buzzer + destello)");
        break;
      case 'b':
        alarma = false;                  // para el destello
        digitalWrite(LED_ALARMA, LOW);
        noTone(BUZZER);                  // apaga el buzzer pasivo
        Serial.println("OK: ALARMA APAGADA");
        break;
      case 'X':
        alarma = false;
        digitalWrite(LED_DIEGO, LOW);
        digitalWrite(LED_FRANCO, LOW);
        digitalWrite(LED_ALARMA, LOW);
        noTone(BUZZER);                  // apaga el buzzer pasivo
        Serial.println("OK: TODO APAGADO");
        break;
    }
  }

  // Destello no bloqueante: mientras 'alarma' este activa, parpadea el LED
  if (alarma && millis() - ultimoCambio >= INTERVALO) {
    ultimoCambio = millis();
    destelloEncendido = !destelloEncendido;
    digitalWrite(LED_ALARMA, destelloEncendido ? HIGH : LOW);
  }
}
