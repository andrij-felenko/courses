#pragma once

#include <chrono>
#include <cstdint>
#include <deque>
#include <string>
#include <vector>

/**
 * @brief Структура для зберігання статистики якості зв'язку через ковзне кільце у реальному часі.
 */
struct SlipRingStatistics {
    uint64_t total_sent = 0;            // Загальна кількість відправлених пакетів
    uint64_t total_received = 0;        // Загальна кількість успішно прийнятих пакетів
    uint64_t total_lost = 0;            // Загальна кількість втрачених пакетів
    double packet_loss_percent = 0.0;   // Відсоток втрат пакетів (%)
    double average_latency_ms = 0.0;    // Середня затримка (мс)
    double jitter_ms = 0.0;             // Ковзний джиттер (sliding window jitter) в мс
    uint64_t micro_breaks_detected = 0; // Кількість виявлених мікророзривів контакту
};

/**
 * @brief Клас для моніторингу та аналізу якості Ethernet-зв'язку через капсульне ковзне кільце.
 */
class SlipRingMonitor {
public:
    /**
     * @brief Конструктор монітора.
     * @param window_size Розмір ковзного вікна для розрахунку джитеру та затримки.
     * @param micro_break_threshold_ms Поріг затримки для фіксації мікророзриву (мс).
     */
    explicit SlipRingMonitor(size_t window_size = 100, double micro_break_threshold_ms = 50.0);

    /**
     * @brief Реєстрація відправки нового пакету.
     */
    void recordSentPacket(uint64_t sequence_number);

    /**
     * @brief Реєстрація успішного отримання пакету.
     */
    void recordReceivedPacket(uint64_t sequence_number, 
                              std::chrono::steady_clock::time_point send_time, 
                              std::chrono::steady_clock::time_point receive_time);

    /**
     * @brief Реєстрація втрати пакету (таймаут або відсутність відповіді).
     */
    void recordLostPacket(uint64_t sequence_number);

    /**
     * @brief Отримання поточної агрегованої статистики.
     */
    SlipRingStatistics getStatistics() const;

    /**
     * @brief Очищення всієї статистики та буферів.
     */
    void reset();

private:
    size_t window_size_;
    double micro_break_threshold_ms_;

    uint64_t total_sent_;
    uint64_t total_received_;
    uint64_t total_lost_;
    uint64_t micro_breaks_detected_;

    struct LatencyRecord {
        std::chrono::steady_clock::time_point receive_time;
        double latency_ms;
    };

    std::deque<LatencyRecord> latency_window_;
    std::deque<double> jitter_window_;
};
