// stop-and-wait ARQ: шлю критичну команду, поки не прийде ACK
// ACK_TIMEOUT — скільки чекати підтвердження; MAX_TRIES — стеля повторів
bool sendReliable(uint8_t seq, const Cmd& cmd) {
    for (int tries = 0; tries < MAX_TRIES; tries++) {
        sendPacket(seq, cmd);                 // 1) передаю (чи повторно передаю)
        uint32_t t0 = millis();
        while (millis() - t0 < ACK_TIMEOUT) { // 2) чекаю ACK з цим же номером
            if (gotAckFor(seq)) return true;  //    дійшло й підтверджено
        }
        // 3) тиша до таймауту → повтор тієї самої команди з тим самим seq
    }
    return false;                             // 4) MAX_TRIES марно → зв'язок мертвий
}

// ACK_TIMEOUT = 200 мс, MAX_TRIES = 5:
//   спроба 1 @ 0 мс    → тиша 200 мс
//   спроба 2 @ 200 мс  → тиша 200 мс
//   спроба 3 @ 400 мс  → тиша 200 мс
//   спроба 4 @ 600 мс  → тиша 200 мс
//   спроба 5 @ 800 мс  → тиша 200 мс
//   1000 мс: 5 спроб марно → return false → failsafe()
