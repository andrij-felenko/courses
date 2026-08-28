#include "RingBuffer_Config.hpp"
#include <iostream>

int main() {
    RawByteBuffer network_rx_queue;
    network_rx_queue.push(0x7E); // Символ прапорця HDLC
    network_rx_queue.push(0xFF);
    network_rx_queue.push(0x03);

    std::cout << "Розмір черги RX: " << network_rx_queue.size() << " байт\n";

    LogQueue system_events;
    system_events.push("BOOT_OK");
    system_events.push("SENSORS_CALIBRATED");
    system_events.dump("Events");

    // Перевірка функціональної трансформації map:
    auto event_lengths = system_events.map([](const std::string& s) { return s.length(); });
    std::cout << "Довжина першої події: " << event_lengths.front() << "\n";

    // Перевірка конструктора з іншої місткості:
    RingBuffer<std::string, 4> small_event_log(system_events);
    std::cout << "Скопійовано у малий буфер: " << small_event_log.size() << " події\n";

    run_memory_lifecycle_test();
    return 0;
}
