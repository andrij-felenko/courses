// Приклад використання в C++ потоці синхронізації
template <embedded::storage::FlashDriver Driver, uint32_t N>
void sync_telemetry_loop(embedded::storage::FlashRingQueue<Driver, N>& queue, NetworkClient& net) {
    std::array<uint8_t, 256> payload_buffer{};

    while (true) {
        auto peek_res = queue.peek(payload_buffer);
        if (!peek_res.has_value()) {
            if (peek_res.error() == embedded::storage::RingError::Empty) {
                sleep_for(std::chrono::seconds(1));
                continue;
            }
            break;
        }

        const auto payload_span = std::span{payload_buffer.data(), peek_res->payload_len};
        if (net.send_packet(payload_span)) {
            // ACK отримано: фіксуємо вилучення з черги
            queue.commit_pop();
        } else {
            // Обрив зв'язку: експоненційний відступ
            sleep_for(std::chrono::seconds(5));
        }
    }
}
