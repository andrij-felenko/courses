int main() {
    const std::vector<uint8_t> sample_packet = {
        /* Фіксована частина CLNP (9 байтів) */
        0x81,                   /* NLPID = CLNP (0x81) */
        0x19,                   /* LI = 25 байтів заголовка */
        0x01,                   /* Version = 1 */
        0x1E,                   /* Lifetime = 30 (15 секунд) */
        0x1C,                   /* Flags = Non-segmented, Type = Data (0x1C) */
        0x00, 0x27,             /* Segment Length = 39 байтів */
        0xE6, 0xCB,             /* Checksum Fletcher-16 */

        /* Адреса призначення (7 байтів) */
        0x07,                   /* DAL = 7 байтів */
        0x49, 0x00, 0x01, 0x00, 0x1A, 0x2B, 0x01,

        /* Адреса джерела (7 байтів) */
        0x07,                   /* SAL = 7 байтів */
        0x49, 0x00, 0x01, 0x00, 0xAA, 0xBB, 0x01,

        /* Транспортний блок TP4 DT-TPDU (5 байтів) */
        0x04,                   /* TPDU LI = 4 байти */
        0xF0,                   /* Type = DT-TPDU (0xF0) */
        0x12, 0x34,             /* Destination Reference = 0x1234 */
        0x85,                   /* EOT=1, TPDU-NR = 5 */

        /* Корисні дані (Payload): "HELLO OSI" */
        'H', 'E', 'L', 'L', 'O', ' ', 'O', 'S', 'I'
    };

    std::cout << "=== ДЕМОНСТРАЦІЯ РОЗБОРУ СТЕКУ CLNP / TP4 (C++20) ===\n";

    auto clnp_opt = osi::PacketParser::parseClnp(sample_packet);
    if (!clnp_opt) {
        std::cerr << "ПОМИЛКА: Некоректний пакет CLNP або пошкоджена сума Флетчера!\n";
        return 1;
    }

    const auto& clnp = *clnp_opt;
    std::cout << "[CLNP] NLPID: 0x" << std::hex << static_cast<int>(clnp.nlpid) << std::dec << " (CLNP)\n";
    std::cout << "[CLNP] Довжина заголовка: " << static_cast<int>(clnp.header_len)
              << " байтів, Повна довжина: " << clnp.segment_len << " байтів\n";
    std::cout << "[CLNP] Lifetime: " << static_cast<int>(clnp.lifetime)
              << " (" << (clnp.lifetime * 0.5) << " с)\n";

    std::cout << "[CLNP] Призначення NSAP: ";
    clnp.dst_nsap.print();
    std::cout << "\n[CLNP] Джерело NSAP:      ";
    clnp.src_nsap.print();
    std::cout << "\n";

    auto tp4_opt = osi::PacketParser::parseTp4Dt(clnp.payload);
    if (!tp4_opt) {
        std::cerr << "ПОМИЛКА: Не вдалося вилучити заголовок TP4!\n";
        return 1;
    }

    const auto& tp4 = *tp4_opt;
    std::cout << "\n[TP4] Тип TPDU: 0x" << std::hex << static_cast<int>(tp4.type) << std::dec << " (Data TPDU)\n";
    std::cout << "[TP4] Destination Reference: 0x" << std::hex << tp4.dst_ref << std::dec << "\n";
    std::cout << "[TP4] Порядковий номер (TPDU-NR): " << static_cast<int>(tp4.tpdu_nr)
              << ", EOT: " << (tp4.eot ? "TRUE (останній фрагмент)" : "FALSE") << "\n";
    std::cout << "[TP4] Розмір корисних даних: " << tp4.payload.size() << " байтів\n";

    std::string_view msg(reinterpret_cast<const char*>(tp4.payload.data()), tp4.payload.size());
    std::cout << "[TP4] Дані: \"" << msg << "\"\n";

    return 0;
}
