#include <iostream>
#include <thread>
#include <chrono>
#include <random>

int main() {
    using namespace realtime::control;
    using namespace std::chrono_literals;

    LockFreeTripleBuffer<float, 4> tripleBuffer;
    WatchdogConfig cfg{
        .deadlineLimit = 45ms,
        .maxExtrapolation = 100ms,
        .fatalTimeout = 500ms,
        .decayLambda = 15.0f,
        .maxSlewRate = 100.0f
    };
    RealTimeMLController<float, 4> controller(cfg);
    
    FallbackPID<float>::Gains gains{
        .kp = 2.5f, .ki = 0.8f, .kd = 0.15f, .ts = 0.002f, .minVal = -100.0f, .maxVal = 100.0f
    };
    FallbackPID<float> pid(gains);

    std::atomic<bool> running{true};

    auto producer = std::jthread([&](std::stop_token st) {
        uint32_t frameId = 0;
        std::mt19937 rng(1337);
        std::uniform_int_distribution<int> jitterDist(0, 15);

        while (!st.stop_requested() && running.load(std::memory_order_relaxed)) {
            int sleepMs = 30 + jitterDist(rng);
            if (frameId % 20 == 0) sleepMs += 75; // Дедлайн міс

            std::this_thread::sleep_for(std::chrono::milliseconds(sleepMs));

            auto now = std::chrono::duration_cast<Microseconds>(
                std::chrono::steady_clock::now().time_since_epoch()
            );

            PredictionFrame<float, 4> frame{
                .values = { std::sin(frameId * 0.1f) * 10.0f, 0.0f, 0.0f, 0.0f },
                .timestamp = now,
                .frameId = ++frameId,
                .confidence = 0.98f
            };
            tripleBuffer.write(frame);
        }
    });

    auto consumer = std::jthread([&]() {
        uint32_t freshCount = 0, extrapCount = 0, fallbackCount = 0;
        auto nextTick = std::chrono::steady_clock::now();

        for (int i = 0; i < 5000; ++i) {
            auto now = std::chrono::duration_cast<Microseconds>(
                std::chrono::steady_clock::now().time_since_epoch()
            );
            auto [frame, isFresh] = tripleBuffer.read();
            auto [correction, status] = controller.update(frame, isFresh, now);

            switch (status) {
                case ControlStatus::Fresh: freshCount++; break;
                case ControlStatus::Extrapolated: extrapCount++; break;
                case ControlStatus::FallbackPid: fallbackCount++; break;
                default: break;
            }

            nextTick += 2ms;
            std::this_thread::sleep_until(nextTick);
        }

        running.store(false, std::memory_order_relaxed);

        std::cout << "=== C++20 BENCHMARK COMPLETED ===\n";
        std::cout << "Fresh ticks:        " << freshCount << " (" << (freshCount / 50.0f) << "%)\n";
        std::cout << "Extrapolated ticks: " << extrapCount << " (" << (extrapCount / 50.0f) << "%)\n";
        std::cout << "Fallback ticks:     " << fallbackCount << " (" << (fallbackCount / 50.0f) << "%)\n";
        std::cout << "Max Latency:        " << controller.getMaxLatency().count() * 0.001f << " ms\n";
    });

    return 0;
}
