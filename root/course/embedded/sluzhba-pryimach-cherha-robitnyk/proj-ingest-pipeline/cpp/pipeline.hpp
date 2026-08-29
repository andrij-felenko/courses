#pragma once

// Три решти конвеєра: приймач (швидкий, без логіки), вирівнювач часової шкали
// зі сховищем пакетного запису і пул робітників розбору.

#include "bounded_queue.hpp"
#include "metrics.hpp"
#include "wire_format.hpp"

#include <cstddef>
#include <cstdint>
#include <mutex>
#include <optional>
#include <span>
#include <stop_token>
#include <thread>
#include <unordered_map>
#include <vector>

namespace ingest {

inline constexpr std::size_t kMaxDatagram = 1500;                        // MTU Ethernet
inline constexpr std::size_t kBatchRows = 256;                           // рядків у батчі
inline constexpr auto kBatchMaxAge = std::chrono::milliseconds(200);     // стеля витримки батча
inline constexpr auto kPopTimeout = std::chrono::milliseconds(20);       // крок циклу воркера
inline constexpr std::int64_t kMaxLagMs = 5000;                          // більше — це не лаг

// Приймач: зафіксувати t_recv, загорнути байти в конверт, віддати в чергу. Крапка.
// Жодного розбору тут немає навмисно — інакше цикл сокета впирався б у CPU.
class IngestReceiver {
public:
    IngestReceiver(BoundedQueue& queue, Metrics& metrics) : queue_(queue), metrics_(metrics) {}

    bool on_datagram(std::span<const std::uint8_t> bytes, std::uint32_t peer_id);

    // Читання прапорця зворотного тиску — без м'ютекса, лише acquire-завантаження.
    bool paused() const noexcept { return queue_.backpressure(); }

private:
    BoundedQueue& queue_;
    Metrics& metrics_;
};

// Вирівнювання часової шкали: t_event = t_recv - lag.
// Базу «t_recv - uptime» тримаємо за мінімумом спостережень: найшвидша доставка
// найближча до істини, решта затримок — черги в мережі й у нас самих.
class TimeAligner {
public:
    struct Aligned {
        Clock::time_point event_time;
        std::chrono::milliseconds lag;
    };

    Aligned align(std::uint32_t device_id, std::uint32_t uptime_ms, Clock::time_point recv_wall);

private:
    std::mutex mutex_;
    std::unordered_map<std::uint32_t, std::int64_t> base_ms_;
};

// Сховище: приймає лише батчами, бо рядок за рядком база не витримає темпу.
class EventStore {
public:
    explicit EventStore(Metrics& metrics) : metrics_(metrics) {}

    void write_batch(std::span<const NormalizedEvent> rows);

    std::uint64_t rows() const;
    std::uint64_t batches() const;

private:
    Metrics& metrics_;
    mutable std::mutex mutex_;
    std::uint64_t rows_{0};
    std::uint64_t batches_{0};
};

// Пул робітників: розбір, перевірка CRC, вирівнювання часу, фільтр діапазонів, батч.
class WorkerPool {
public:
    WorkerPool(BoundedQueue& queue, TimeAligner& aligner, EventStore& store, Metrics& metrics,
               unsigned count);

    void join();

private:
    void run(std::stop_token stop);
    std::optional<NormalizedEvent> handle(const RawPacket& packet);

    BoundedQueue& queue_;
    TimeAligner& aligner_;
    EventStore& store_;
    Metrics& metrics_;
    std::vector<std::jthread> threads_;
};

}  // namespace ingest
