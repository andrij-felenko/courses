int main() {
    PbcastReceiver node_a(1, 100);
    PbcastReceiver node_b(1, 100);

    const std::string msg1 = "Payload #101";
    const std::string msg2 = "Payload #102";
    const std::string msg3 = "Payload #103 (Lost on A)";
    const std::string msg4 = "Payload #104";

    /* Вузол B отримує всі пакети 101..104 */
    node_b.insert_packet(101, std::span{reinterpret_cast<const uint8_t*>(msg1.data()), msg1.size()});
    node_b.insert_packet(102, std::span{reinterpret_cast<const uint8_t*>(msg2.data()), msg2.size()});
    node_b.insert_packet(103, std::span{reinterpret_cast<const uint8_t*>(msg3.data()), msg3.size()});
    node_b.insert_packet(104, std::span{reinterpret_cast<const uint8_t*>(msg4.data()), msg4.size()});

    /* Вузол A пропускає #103 */
    node_a.insert_packet(101, std::span{reinterpret_cast<const uint8_t*>(msg1.data()), msg1.size()});
    node_a.insert_packet(102, std::span{reinterpret_cast<const uint8_t*>(msg2.data()), msg2.size()});
    node_a.insert_packet(104, std::span{reinterpret_cast<const uint8_t*>(msg4.data()), msg4.size()});

    std::cout << "Стан A до gossip: LowWatermark=" << node_a.low_watermark() 
              << ", Mask=" << node_a.received_mask() << "\n";

    Digest digest_b{
        .sender_id = node_b.sender_id(),
        .low_watermark = node_b.low_watermark(),
        .received_mask = node_b.received_mask()
    };

    auto missing = calculate_missing_sequences(node_a, digest_b);
    std::cout << "Вузол A знайшов " << missing.size() << " пропусків. Перший: " << missing.front() << "\n";

    /* Затягування відсутнього пакета з буфера B */
    if (!missing.empty()) {
        auto repair_data = node_b.get_packet(missing.front());
        if (repair_data.has_value()) {
            node_a.insert_packet(missing.front(), *repair_data);
        }
    }

    std::cout << "Стан A після ремонту: LowWatermark=" << node_a.low_watermark() 
              << ", Mask=" << node_a.received_mask() << " (Повна збіжність!)\n";

    return 0;
}
