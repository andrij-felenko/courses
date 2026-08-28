#include <DFRobot_AS3935_I2C.h>

// ── Плата: під свій мікроконтролер ─────────────────────────────
#if defined(ESP32) || defined(ESP8266)
  #define IRQ_PIN            4        // будь-який GPIO з перериванням
#else
  #define IRQ_PIN            2        // Uno/Nano: тільки 2 або 3
#endif

#define AS3935_I2C_ADDR      AS3935_ADD3   // ЗВІРИТИ з DIP-перемикачем!

// ── Налаштування під місце ─────────────────────────────────────
#define AS3935_CAPACITANCE   96       // стартова ємність, пФ (кратна 8)

DFRobot_AS3935_I2C  lightning(IRQ_PIN, AS3935_I2C_ADDR);

volatile bool irqTriggered = false;   // прапорець із обробника переривання
