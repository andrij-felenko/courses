#include "pipeline.hpp"

#include <iostream>
#include <utility>

namespace ingest {

bool IngestReceiver::on_datagram(std::span<const std::uint8_t> bytes, std::uint32_t peer_id) {
    // Сміття з сокета далі приймача не йде: розмір — єдина перевірка, яку ми тут робимо.
    if (bytes.empty() || bytes.size() > kMaxDatagram) {
        metrics_.on_rejected(FrameError::bad_size);
        return false;
    }

    RawPacket packet;
    packet.data.assign(bytes.begin(), bytes.end());  // єдина копія на весь шлях пакета
    packet.recv_wall = Clock::now();
    packet.recv_mono = SteadyClock::now();
    packet.peer_id = peer_id;

    switch (queue_.push(std::move(packet))) {
        case PushStatus::stored:
            metrics_.on_ingested();
            return true;
        case PushStatus::evicted_oldest:
            // Пакет узяли, але за нього заплатили найстарішим у черзі.
            metrics_.on_ingested();
            metrics_.on_dropped();
            return true;
        case PushStatus::rejected_closed:
            metrics_.on_dropped();
            return false;
    }
    return false;
}

TimeAligner::Aligned TimeAligner::align(std::uint32_t device_id, std::uint32_t uptime_ms,
                                        Clock::time_point recv_wall) {
    const auto recv_ms =
        std::chrono::duration_cast<std::chrono::milliseconds>(recv_wall.time_since_epoch()).count();
    const std::int64_t observed = recv_ms - static_cast<std::int64_t>(uptime_ms);

    std::int64_t base = 0;
    {
        std::lock_guard<std::mutex> lock(mutex_);
        auto [it, inserted] = base_ms_.try_emplace(device_id, observed);
        // Менша база — швидша доставка, беремо її. Стрибок понад стелю означає
        // перезавантаження пристрою (uptime почався з нуля) — базу перезаводимо.
        if (!inserted && (observed < it->second || observed - it->second > kMaxLagMs)) {
            it->second = observed;
        }
        base = it->second;
    }

    const std::chrono::milliseconds lag{observed - base};
    return Aligned{recv_wall - lag, lag};
}

void EventStore::write_batch(std::span<const NormalizedEvent> rows) {
    if (rows.empty()) {
        return;
    }
    std::lock_guard<std::mutex> lock(mutex_);
    rows_ += rows.size();
    ++batches_;
    metrics_.on_stored(rows.size());

    // Не логуємо кожен батч: під навантаженням лог сам стає вузьким місцем.
    if (batches_ % 64 == 0) {
        const NormalizedEvent& last = rows.back();
        std::cout << "[сховище] батч #" << batches_ << ": " << rows.size() << " рядків, останній "
                  << last.device_id << " seq=" << last.seq << " lag=" << last.lag.count()
                  << " мс\n";
    }
}

std::uint64_t EventStore::rows() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return rows_;
}

std::uint64_t EventStore::batches() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return batches_;
}

WorkerPool::WorkerPool(BoundedQueue& queue, TimeAligner& aligner, EventStore& store,
                       Metrics& metrics, unsigned count)
    : queue_(queue), aligner_(aligner), store_(store), metrics_(metrics) {
    threads_.reserve(count);
    for (unsigned i = 0; i < count; ++i) {
        threads_.emplace_back([this](std::stop_token stop) { run(std::move(stop)); });
    }
}

void WorkerPool::join() {
    for (auto& thread : threads_) {
        if (thread.joinable()) {
            thread.join();
        }
    }
    threads_.clear();
}

std::optional<NormalizedEvent> WorkerPool::handle(const RawPacket& packet) {
    // Затримка — від моменту прийому до моменту розбору: у ній сидить час у черзі.
    metrics_.observe_latency(SteadyClock::now() - packet.recv_mono);

    const DecodeResult decoded = decode_frame(packet.data);
    if (!decoded) {
        metrics_.on_rejected(decoded.error);
        return std::nullopt;
    }
    if (!in_physical_range(decoded.frame)) {
        metrics_.on_out_of_range();
        return std::nullopt;
    }

    const auto aligned =
        aligner_.align(decoded.frame.device_id, decoded.frame.uptime_ms, packet.recv_wall);

    NormalizedEvent event;
    event.device_id = format_device_id(decoded.frame.device_id);
    event.event_time = aligned.event_time;
    event.lag = aligned.lag;
    event.temperature_c = decoded.frame.temperature_c;
    event.humidity_pct = decoded.frame.humidity_pct;
    event.battery_v = decoded.frame.battery_v;
    event.seq = decoded.frame.seq;
    return event;
}

void WorkerPool::run(std::stop_token stop) {
    std::vector<NormalizedEvent> batch;
    batch.reserve(kBatchRows);
    auto last_flush = SteadyClock::now();

    while (!stop.stop_requested()) {
        RawPacket packet;
        const PopStatus status = queue_.pop(packet, kPopTimeout);
        if (status == PopStatus::closed) {
            break;
        }
        if (status == PopStatus::ok) {
            if (auto event = handle(packet)) {
                batch.push_back(std::move(*event));
            }
        }

        // Батч їде або коли набрався, або коли перший рядок у ньому зачекався:
        // без другої умови рідкий трафік лежав би в пам'яті годинами.
        const auto now = SteadyClock::now();
        if (batch.size() >= kBatchRows || (!batch.empty() && now - last_flush >= kBatchMaxAge)) {
            store_.write_batch(batch);
            batch.clear();
            last_flush = now;
        }
    }

    // Коректне завершення: допиваємо чергу до дна і аж тоді скидаємо залишок батча.
    RawPacket packet;
    while (queue_.pop(packet, std::chrono::milliseconds(0)) == PopStatus::ok) {
        if (auto event = handle(packet)) {
            batch.push_back(std::move(*event));
        }
        if (batch.size() >= kBatchRows) {
            store_.write_batch(batch);
            batch.clear();
        }
    }
    store_.write_batch(batch);
}

}  // namespace ingest
