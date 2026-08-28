int main() {
    using namespace quic;
    std::cout << "=== ДЕМОНСТРАЦІЯ ДЕФРАГМЕНТАЦІЇ QUIC ТА QPACK (C++) ===\n\n";

    QuicStreamReassembler stream(0, 65536);

    // 1. Прибуває пакет з другого фрагмента (Offset=10)
    std::vector<uint8_t> pkt2 = {'W', 'o', 'r', 'l', 'd', '_', 'H', 'T', 'T', 'P', '3', '!'};
    std::cout << "1. Отримано пакет 2 (Offset=10, Len=12)\n";
    stream.insert_frame(10, pkt2, false);

    auto read1 = stream.read_contiguous();
    std::cout << "   Прочитано байтів: " << read1.size() << " (чекаємо на Offset=0)\n\n";

    // 2. Прибуває перший пакет (Offset=0) з QPACK індексом 15
    std::vector<uint8_t> pkt1 = {15, 'H', 'e', 'l', 'l', 'o', '_', 'Q', 'U', 'I'};
    std::cout << "2. Отримано пакет 1 (Offset=0, Len=10)\n";
    stream.insert_frame(0, pkt1, false);

    auto read2 = stream.read_contiguous();
    std::cout << "   Прочитано байтів: " << read2.size() << " (суцільний ряд зібрано!)\n";
    if (!read2.empty()) {
        QuicStreamReassembler::decode_qpack_indexed(read2[0]);
        std::string_view payload(reinterpret_cast<const char*>(read2.data() + 1), read2.size() - 1);
        std::cout << "   Вміст потоку: " << payload << "\n\n";
    }

    return 0;
}
