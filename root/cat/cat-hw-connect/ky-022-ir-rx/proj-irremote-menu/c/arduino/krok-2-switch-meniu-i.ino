#include <IRremote.hpp>

const uint8_t IR_PIN = 2;
const uint16_t MY_REMOTE = 0x00;   // адреса ТВОГО пульта (знята скелетом)

// коди кнопок ЦЬОГО пульта
enum Button : uint16_t {
  BTN_1     = 0x45,
  BTN_2     = 0x46,
  BTN_PLAY  = 0x40,
  BTN_UP    = 0x15,
  BTN_DOWN  = 0x07,
};

uint8_t brightness = 128;          // стан, яким керуємо (0..255)

void applyBrightness() {
  analogWrite(9, brightness);      // реальна дія: яскравість LED на піні D9
  Serial.print("яскравість = ");
  Serial.println(brightness);
}

void setup() {
  Serial.begin(115200);
  pinMode(9, OUTPUT);
  IrReceiver.begin(IR_PIN, ENABLE_LED_FEEDBACK);
  applyBrightness();
}

void loop() {
  if (IrReceiver.decode()) {
    // чужий пульт? — ігноруємо, але буфер звільнити ОБОВ'ЯЗКОВО
    if (IrReceiver.decodedIRData.address != MY_REMOTE) {
      IrReceiver.resume();
      return;
    }

    switch (IrReceiver.decodedIRData.command) {
      case BTN_UP:
        if (brightness <= 245) brightness += 10;
        applyBrightness();
        break;
      case BTN_DOWN:
        if (brightness >= 10) brightness -= 10;
        applyBrightness();
        break;
      case BTN_PLAY:
        brightness = (brightness == 0) ? 128 : 0;   // вимк/увімк
        applyBrightness();
        break;
      case BTN_1: Serial.println("режим 1"); break;
      case BTN_2: Serial.println("режим 2"); break;
      default:
        Serial.print("невідома кнопка: 0x");
        Serial.println(IrReceiver.decodedIRData.command, HEX);
        break;
    }
    IrReceiver.resume();
  }
}
