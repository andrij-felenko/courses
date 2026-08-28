int main() {
    UartOversamplingReceiver<OversamplingMode::Ratio16x> rx;

    std::cout << "=== ТЕСТ 1: Фільтрація імпульсної завади (Glitch Filter) ===\n";
    rx.tick(1);
    rx.tick(0); // Спад
    rx.tick(0);
    for (int t = 2; t < 16; ++t) {
        rx.tick(1); // Відновлення лінії в 1
    }
    if (rx.wasGlitchRejected()) {
        std::cout << "✓ Успіх: заваду відфільтровано, FSM повернувся в Idle\n\n";
    }

    std::cout << "=== ТЕСТ 2: Мажоритарне відновлення зашумленого біта ===\n";
    rx.reset();
    // Старт-біт (16 нулів)
    for (int t = 0; t < 16; ++t) rx.tick(0);
    // D0 (рівень 1, на такті 8 сплеск 0)
    for (int t = 0; t < 16; ++t) {
        uint8_t pin = (t == 8) ? 0 : 1;
        rx.tick(pin);
    }
    // D1..D7 (чисті нулі)
    for (int b = 1; b < 8; ++b) {
        for (int t = 0; t < 16; ++t) rx.tick(0);
    }
    // Стоп-біт (одиниці)
    std::optional<RxFrameResult> frame;
    for (int t = 0; t < 16; ++t) {
        auto res = rx.tick(1);
        if (res) frame = res;
    }

    if (frame.has_value()) {
        std::cout << "✓ Отримано байт: 0x" << std::hex << std::uppercase << std::setw(2)
                  << std::setfill('0') << static_cast<int>(frame->data) << "\n";
        std::cout << "✓ Прапорець шуму NF: " << std::boolalpha << frame->noise_flag << "\n";
        std::cout << "✓ Помилка кадру FE: " << frame->framing_error << "\n";
    }

    return 0;
}
