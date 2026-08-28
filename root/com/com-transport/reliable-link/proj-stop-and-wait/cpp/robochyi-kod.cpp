#include <stdint.h>

struct Cmd { uint8_t op; int16_t arg; };

// Шлю критичну команду stop-and-wait. true — підтверджено, false — зв'язок мертвий.
bool sendReliable(uint8_t seq, const Cmd& cmd) {
    for (int tries = 0; tries < MAX_TRIES; tries++) {
        sendPacket(seq, cmd);                  // 1) передаю (чи повторно — той самий seq)
        uint32_t t0 = millis();
        while (millis() - t0 < ACK_TIMEOUT) {  // 2) чекаю ACK саме з цим номером
            if (gotAckFor(seq)) return true;   //    дійшло й підтверджено
        }
        // 3) тиша до таймауту → наступна ітерація повторить той самий seq
    }
    return false;                              // 4) MAX_TRIES марно → обрив
}
