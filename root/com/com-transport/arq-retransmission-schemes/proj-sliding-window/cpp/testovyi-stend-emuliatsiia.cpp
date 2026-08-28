/* Сценарій емуляції ненадійного каналу та роботи Selective Repeat у C++ */
int main() {
    using namespace arq;
    SelectiveRepeatSender tx;
    SelectiveRepeatReceiver rx;

    std::cout << "========================================\n";
    std::cout << "  Симуляція Selective Repeat (C++)\n";
    std::cout << "========================================\n";

    std::vector<uint8_t> payload = {'T', 'E', 'L', 'E', 'M', 'E', 'T', 'R', 'Y'};

    // Крок 1. Відправляємо пачку кадрів 0, 1, 2, 3
    std::vector<Frame> in_flight;
    for (int i = 0; i < 4; ++i) {
        if (auto f = tx.send(payload)) {
            std::cout << "[TX] Відправлено Кадр #" << static_cast<int>(f->seq)
                      << " (TX Base = " << static_cast<int>(tx.base()) << ")\n";
            in_flight.push_back(*f);
        }
    }

    std::vector<std::vector<uint8_t>> delivered;

    // Крок 2. Кадри 0 та 1 благополучно доходять
    for (int i = 0; i < 2; ++i) {
        if (auto ack = rx.on_frame(in_flight[i], delivered)) {
            std::cout << "[RX] Прийнято #" << static_cast<int>(in_flight[i].seq)
                      << " -> Шлемо вибірковий ACK " << static_cast<int>(ack->ack) << "\n";
            tx.on_ack(*ack);
        }
    }

    // Крок 3. Кадр 2 губиться в каналі
    std::cout << "\n>>> [КАНАЛ] ✗ Кадр #2 ВТРАЧЕНО В ЕФІРІ! <<<\n\n";

    // Крок 4. Кадр 3 прибуває до приймача: він зберігається в буфері!
    if (auto ack = rx.on_frame(in_flight[3], delivered)) {
        std::cout << "[RX] Отримано Кадр #3 поза чергою -> ЗБЕРЕЖЕНО В БУФЕРІ!\n";
        std::cout << "[RX] Відправлено вибірковий ACK " << static_cast<int>(ack->ack) << "\n";
        tx.on_ack(*ack);
    }

    // Крок 5. На передавачі вичерпується таймаут для кадру #2
    std::cout << "\n[TX] Очікування таймауту для Кадру #2...\n";
    std::vector<Frame> retrans;
    for (int t = 0; t < RTO_TICKS; ++t) {
        retrans = tx.tick();
        if (!retrans.empty()) break;
    }

    // Крок 6. Передавач повторює ЛИШЕ кадр #2 (не чіпаючи #3!)
    std::cout << "[TX] Спрацював RTO! Точковий повтор " << retrans.size() << " кадру(ів):\n";
    for (const auto& rf : retrans) {
        std::cout << "     -> Повтор виключно втраченого кадру #" 
                  << static_cast<int>(rf.seq) << "\n";
    }

    // Крок 7. Повторений кадр #2 прибуває: приймач склеює буфер і видає обидва повідомлення!
    if (auto ack = rx.on_frame(retrans[0], delivered)) {
        std::cout << "\n[RX] Отримано пропущений Кадр #2! Буфер розблоковано!\n";
        std::cout << "[RX] Застосунку доставлено повідомлень: " << delivered.size() 
                  << " (номери #0, #1, #2, #3 по порядку)\n";
        tx.on_ack(*ack);
    }

    std::cout << "\n[Підсумок] Поточний стан: TX Base = " << static_cast<int>(tx.base())
              << ", RX Base = " << static_cast<int>(rx.base()) << "\n";

    return 0;
}
