// Прогін конвеєра під двома різними джерелами: ввічливим (чує зворотний тиск)
// і залповим (не чує). Другий і показує, коли спрацьовує витіснення найстарішого.

#include "bounded_queue.hpp"
#include "metrics.hpp"
#include "pipeline.hpp"
#include "wire_format.hpp"

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <thread>
#include <vector>

namespace {

using namespace ingest;

struct Source {
    std::uint32_t device_id;
    std::uint32_t uptime_ms;
    std::uint16_t seq;
};

// Кадр із реального пристрою — з тими самими вадами, що трапляються в полі:
// збитий біт, утрачена межа кадру і давач, який поїхав за фізичну межу.
std::vector<std::uint8_t> make_frame(Source& source, std::size_t index) {
    source.uptime_ms += 100;  // пристрій шле раз на 100 мс

    auto raw_temp = static_cast<std::int16_t>(2345 + (index % 40));  // ~23.45 °C
    auto raw_hum = static_cast<std::uint16_t>(5820 + (index % 15));  // ~58.2 %
    const std::uint16_t raw_vbat = 3820;                             // 3.82 В

    if (index % 53 == 0) {
        raw_temp = 20000;  // 200 °C — давач відвалився, дані невалідні
    }

    auto frame = encode_frame(source.device_id, source.uptime_ms, raw_temp, raw_hum, raw_vbat,
                              source.seq++, 0x0007);

    if (index % 97 == 0) {
        frame[13] ^= 0x01;  // біт помер у каналі — CRC не зійдеться
    }
    if (index % 211 == 0) {
        frame[0] = 0x00;  // збилася межа кадру — магія не та
    }
    return frame;
}

}  // namespace

int main() {
    Metrics metrics;
    BoundedQueue queue(1024);
    TimeAligner aligner;
    EventStore store(metrics);
    IngestReceiver receiver(queue, metrics);
    WorkerPool pool(queue, aligner, store, metrics, 4);

    std::array<Source, 4> sources{Source{0x000104A2, 0, 0}, Source{0x000104A3, 0, 0},
                                 Source{0x000104B0, 0, 0}, Source{0x00020001, 0, 0}};

    constexpr std::size_t kPoliteFrames = 20000;
    constexpr std::size_t kFloodFrames = 5000;

    const auto started = SteadyClock::now();
    std::uint64_t throttle_waits = 0;

    std::cout << "Конвеєр прийому телеметрії: 4 воркери, черга на 1024 пакети\n";

    // Фаза 1: TCP-подібне джерело. Побачив зворотний тиск — притримав читання сокета.
    for (std::size_t i = 0; i < kPoliteFrames; ++i) {
        while (receiver.paused()) {
            ++throttle_waits;
            std::this_thread::sleep_for(std::chrono::microseconds(200));
        }
        const auto frame = make_frame(sources[i % sources.size()], i);
        receiver.on_datagram(frame, static_cast<std::uint32_t>(i % 64));
    }

    // Фаза 2: UDP-залп. Притримати відправника неможливо — черга рятується сама.
    for (std::size_t i = 0; i < kFloodFrames; ++i) {
        const auto frame = make_frame(sources[i % sources.size()], i);
        receiver.on_datagram(frame, static_cast<std::uint32_t>(i % 64));
    }

    queue.close();  // приймач замовк
    pool.join();    // воркери допивають чергу і скидають батчі

    const auto elapsed =
        std::chrono::duration_cast<std::chrono::milliseconds>(SteadyClock::now() - started).count();
    const double seconds = elapsed > 0 ? elapsed / 1000.0 : 0.001;

    std::cout << "\n--- Підсумок прийому ---\n"
              << "Надіслано кадрів:      " << (kPoliteFrames + kFloodFrames) << "\n"
              << "Прийнято в чергу:      " << metrics.ingested_total() << "\n"
              << "Витіснено з черги:     " << metrics.dropped_total() << "\n"
              << "Пауз зворотного тиску: " << throttle_waits << "\n"
              << "Биті CRC:              " << metrics.rejected_total(FrameError::crc_mismatch)
              << "\n"
              << "Збита межа кадру:      " << metrics.rejected_total(FrameError::bad_magic) << "\n"
              << "Поза діапазоном:       " << metrics.out_of_range_total() << "\n"
              << "Записано рядків:       " << store.rows() << " у " << store.batches()
              << " батчах\n"
              << "Час прогону:           " << elapsed << " мс\n"
              << "Темп:                  " << ((kPoliteFrames + kFloodFrames) / seconds)
              << " кадрів/с\n\n"
              << metrics.render();
    return 0;
}
