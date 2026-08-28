#include <iostream>
#include <thread>
#include <vector>

struct TelemetryMetric {
    uint64_t timestamp_ns;
    uint32_t sensor_id;
    float value;
};

void run_ingestion_pipeline() {
    constexpr std::size_t CHANNEL_CAPACITY = 10000;
    BoundedChannel<TelemetryMetric> channel(CHANNEL_CAPACITY);

    // Продюсер: мережевий приймач пакетів
    std::thread producer([&channel]() {
        for (uint32_t i = 1; i <= 100000; ++i) {
            TelemetryMetric metric{
                .timestamp_ns = 1700000000000000ULL + i,
                .sensor_id = i % 500,
                .value = 24.5f + static_cast<float>(i % 10) * 0.1f
            };
            if (!channel.send(metric)) {
                break; // Канал закрито
            }
        }
        channel.close();
    });

    // Споживачі: пул воркерів збереження
    constexpr int NUM_WORKERS = 4;
    std::vector<std::thread> workers;

    for (int w = 0; w < NUM_WORKERS; ++w) {
        workers.emplace_back([&channel, w]() {
            std::vector<TelemetryMetric> batch;
            batch.reserve(100);

            while (true) {
                auto metric = channel.recv();
                if (!metric.has_value()) {
                    break; // Чергу вичерпано і канал закрито
                }

                batch.push_back(*metric);
                if (batch.size() >= 100) {
                    // Імітація пакетного збереження в БД
                    batch.clear();
                }
            }
        });
    }

    producer.join();
    for (auto& worker : workers) {
        worker.join();
    }
}
