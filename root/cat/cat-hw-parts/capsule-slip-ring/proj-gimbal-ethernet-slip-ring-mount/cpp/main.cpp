#include "slip_ring_monitor.hpp"
#include <iostream>
#include <thread>
#include <chrono>
#include <random>
#include <iomanip>

/**
 * @brief Головна точка входу для демонстрації роботи монітора якості зв'язку
 *        через капсульне ковзне кільце (Slip Ring) під час обертання.
 */
int main() {
    std::cout << "=== Симуляція моніторингу Ethernet зв'язку через капсульне ковзне кільце ===\n";

    // Створюємо монітор з вікном у 50 пакетів та порогом мікророзриву 25 мс
    SlipRingMonitor monitor(50, 25.0);

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> loss_dist(0.0, 1.0);
    std::uniform_real_distribution<> jitter_dist(2.0, 15.0);
    std::uniform_real_distribution<> micro_break_dist(0.0, 1.0);

    const int total_iterations = 120;
    uint64_t seq_num = 1;

    for (int step = 1; step <= total_iterations; ++step) {
        auto send_time = std::chrono::steady_clock::now();
        monitor.recordSentPacket(seq_num);

        // Імітуємо механічне обертання та вібрацію: періодично виникають мікророзриви
        bool high_vibration_zone = (step % 30 >= 20 && step % 30 <= 25);
        double loss_probability = high_vibration_zone ? 0.25 : 0.03;
        double break_probability = high_vibration_zone ? 0.40 : 0.05;

        double base_delay = 5.0 + jitter_dist(gen);

        if (loss_dist(gen) < loss_probability) {
            monitor.recordLostPacket(seq_num);
            std::cout << "[ПОПЕРЕДЖЕННЯ] Крок " << std::setw(3) << step 
                      << " | Пакет #" << seq_num << " ВТРАЧЕНО (механічний мікророзрив контакту)!\n";
        } else {
            if (micro_break_dist(gen) < break_probability) {
                base_delay += 40.0; // Перевищує поріг мікророзриву у 25 мс
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(static_cast<int>(base_delay)));
            auto receive_time = std::chrono::steady_clock::now();

            monitor.recordReceivedPacket(seq_num, send_time, receive_time);
        }

        seq_num++;

        // Виводимо поточну статистику кожні 10 кроків
        if (step % 10 == 0) {
            auto stats = monitor.getStatistics();
            std::cout << "--------------------------------------------------\n"
                      << "[СТАТИСТИКА на крок " << step << "]\n"
                      << "  Відправлено: " << stats.total_sent << "\n"
                      << "  Отримано:   " << stats.total_received << "\n"
                      << "  Втрачено:   " << stats.total_lost << " (" << std::fixed << std::setprecision(2) << stats.packet_loss_percent << "%)\n"
                      << "  Сер. затримка: " << stats.average_latency_ms << " мс\n"
                      << "  Ковзний джиттер: " << stats.jitter_ms << " мс\n"
                      << "  Виявлено мікророзривів: " << stats.micro_breaks_detected << "\n"
                      << "--------------------------------------------------\n";
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }

    std::cout << "=== Симуляція завершена успішно ===\n";
    return 0;
}
