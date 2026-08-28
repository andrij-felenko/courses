struct Pending {
    uint16_t cmd;                 // яку команду чекаємо підтвердити
    uint8_t  tries    = 0;        // воно ж поле confirmation у кадрі
    uint64_t deadline = 0;        // коли вважати, що відповіді вже не буде
    bool     acked    = false;
    bool     failed   = false;
};

void tick(Pending &p, uint64_t now_ms) {
    if (p.acked || p.failed || now_ms < p.deadline) return;
    if (p.tries >= 3) { p.failed = true; return; }   // стільки ж дає QGroundControl
    send_command(p.cmd, p.tries);                    // confirmation = номер спроби
    ++p.tries;
    p.deadline = now_ms + 1000;                      // мс
}
