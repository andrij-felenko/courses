#include <IRremote.hpp>

const uint8_t IR_PIN = 2;
const uint16_t BTN_UP = 0x15, BTN_DOWN = 0x07;
const uint16_t MY_REMOTE = 0x00;

uint8_t  brightness   = 128;
uint16_t heldCommand  = 0;          // яку кнопку тримають (0 = жодну)
uint32_t lastActionMs = 0;          // коли востаннє крутили значення
uint32_t lastFrameMs  = 0;          // коли ОСТАННІЙ РАЗ прилетів наш кадр/повтор
const uint16_t REPEAT_MS  = 120;    // ВЛАСНИЙ темп автоповтору, мс
const uint16_t RELEASE_MS = 250;    // тиша довша за це = кнопку відпустили

void applyBrightness() {
  analogWrite(9, brightness);
  Serial.println(brightness);
}

// одна «дія кнопки» — крок регулювання
void stepButton(uint16_t cmd) {
  if (cmd == BTN_UP   && brightness <= 250) brightness += 5;
  if (cmd == BTN_DOWN && brightness >= 5)   brightness -= 5;
  applyBrightness();
}

void setup() {
  Serial.begin(115200);
  pinMode(9, OUTPUT);
  IrReceiver.begin(IR_PIN, ENABLE_LED_FEEDBACK);
}

void loop() {
  // 1) прийшов кадр (перший чи повтор) — відзначаємо, що кнопку ще тримають
  if (IrReceiver.decode()) {
    if (IrReceiver.decodedIRData.address == MY_REMOTE) {
      uint16_t cmd = IrReceiver.decodedIRData.command;   // на повторі теж валідне
      bool isRepeat = IrReceiver.decodedIRData.flags & IRDATA_FLAGS_IS_REPEAT;

      lastFrameMs = millis();        // будь-який наш кадр = «кнопка ще жива»
      if (!isRepeat) {               // новий натиск: діємо одразу й беремо кнопку «на утримання»
        heldCommand  = cmd;
        stepButton(cmd);
        lastActionMs = millis();
      }
      // повтор сам нічого не крутить — темп автоповтору тримаємо нижче, за часом
    }
    IrReceiver.resume();
  }

  // 2) поки кнопку тримають — крутимо значення СВОЇМ темпом
  if (heldCommand != 0 && millis() - lastActionMs >= REPEAT_MS) {
    stepButton(heldCommand);
    lastActionMs = millis();
  }

  // 3) якщо кадрів/повторів давно нема — кнопку відпустили
  if (heldCommand != 0 && millis() - lastFrameMs > RELEASE_MS) {
    heldCommand = 0;                 // тиша → рух спиняється
  }
}
