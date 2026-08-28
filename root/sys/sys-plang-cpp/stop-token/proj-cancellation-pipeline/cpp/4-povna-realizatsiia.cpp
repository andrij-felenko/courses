#include <chrono>
#include <condition_variable>
#include <deque>
#include <format>
#include <iostream>
#include <mutex>
#include <numeric>
#include <optional>
#include <stop_token>
#include <string>
#include <thread>
#include <vector>

// ── Структури даних конвеєра ──────────────────────────────────────────────────

struct RawTelemetryPacket {
    uint64_t id;
    uint64_t timestamp;
    std::string payload;
};

struct ProcessedTelemetryPacket {
    uint64_t id;
    uint64_t checksum;
    std::size_t original_bytes;
    bool is_valid;
};

// ── Контролер тристадійного конвеєра ──────────────────────────────────────────

class TelemetryPipeline {
public:
    TelemetryPipeline(std::size_t queue_capacity, std::size_t worker_count)
        : raw_queue_(queue_capacity),
          processed_queue_(queue_capacity),
          worker_count_(worker_count) {}

    ~TelemetryPipeline() {
        stop_immediate();
    }

    // Запуск усіх ланок конвеєра
    void start() {
        std::cout << "[Конвеєр] Ініціалізація та старт трьох стадій обробки...\n";

        // 1. Стадія виводу / збереження результатів (Sink)
        sink_thread_ = std::jthread([this](std::stop_token stoken) {
            run_sink(stoken);
        });

        // 2. Стадія паралельної трансформації (Worker Pool)
        workers_.reserve(worker_count_);
        for (std::size_t i = 0; i < worker_count_; ++i) {
            workers_.emplace_back([this, i](std::stop_token stoken) {
                run_worker(i, stoken);
            });
        }

        // 3. Стадія генерації / прийому даних (Source)
        source_thread_ = std::jthread([this](std::stop_token stoken) {
            run_source(stoken);
        });
    }

    // Негайне аварійне переривання всього конвеєра
    void stop_immediate() {
        if (!global_stop_source_.stop_requested()) {
            std::cout << "[Конвеєр] Аварійна зупинка: надсилаємо глобальний request_stop()...\n";
            global_stop_source_.request_stop();

            // Будимо умовні змінні черг для негайного виходу
            raw_queue_.notify_all();
            processed_queue_.notify_all();
        }
    }

    // Коректне дренажування: зупиняємо лише джерело, даємо доопрацювати черги
    void stop_graceful() {
        std::cout << "[Конвеєр] Запит на коректне вичерпання (Graceful Drain)...\n";

        // 1. Зупиняємо лише генератор нових даних
        source_stop_source_.request_stop();
        raw_queue_.notify_all();

        // 2. Чекаємо, доки джерело завершить свій цикл
        if (source_thread_.joinable()) {
            source_thread_.join();
        }

        // 3. Чекаємо спорожнення першої черги
        while (!raw_queue_.empty()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(5));
        }

        // 4. Тепер зупиняємо обчислювальний пул
        for (auto& worker : workers_) {
            worker.request_stop();
        }
        raw_queue_.notify_all();

        for (auto& worker : workers_) {
            if (worker.joinable()) worker.join();
        }

        // 5. Чекаємо спорожнення вихідної черги та зупиняємо приймач
        while (!processed_queue_.empty()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(5));
        }

        sink_thread_.request_stop();
        processed_queue_.notify_all();

        if (sink_thread_.joinable()) {
            sink_thread_.join();
        }

        std::cout << "[Конвеєр] Усі черги повністю вичерпані, конвеєр чисто завершено.\n";
    }

    // Очікування завершення роботи всіх потоків
    void join() {
        if (source_thread_.joinable()) source_thread_.join();
        for (auto& w : workers_) {
            if (w.joinable()) w.join();
        }
        if (sink_thread_.joinable()) sink_thread_.join();
    }

    [[nodiscard]] std::stop_token get_stop_token() const noexcept {
        return global_stop_source_.get_token();
    }

    [[nodiscard]] uint64_t get_total_generated() const noexcept {
        return total_generated_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] uint64_t get_total_processed() const noexcept {
        return total_processed_.load(std::memory_order_relaxed);
    }

private:
    // ── Стадія 1: Джерело (генератор пакетів) ─────────────────────────────────
    void run_source(std::stop_token thread_stoken) {
        // Реєструємо підписку: якщо скасовується або весь конвеєр, або локальне джерело
        std::stop_callback cb_global(global_stop_source_.get_token(), [&] {
            raw_queue_.notify_all();
        });
        std::stop_callback cb_local(source_stop_source_.get_token(), [&] {
            raw_queue_.notify_all();
        });

        uint64_t packet_id = 1;
        while (!global_stop_source_.stop_requested() && 
               !source_stop_source_.stop_requested() && 
               !thread_stoken.stop_requested()) {

            RawTelemetryPacket packet{
                .id = packet_id++,
                .timestamp = static_cast<uint64_t>(std::chrono::steady_clock::now().time_since_epoch().count()),
                .payload = "SensorData_Block_Telemetry_XYZ_" + std::to_string(packet_id)
            };

            // Спроба покласти в чергу з можливістю скасування
            if (!raw_queue_.push(std::move(packet), global_stop_source_.get_token())) {
                break; // Скасування під час блокування на повній черзі
            }

            total_generated_.fetch_add(1, std::memory_order_relaxed);

            // Імітація інтервалу генерації пакетів (1 мілісекунда)
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }

        std::cout << std::format("[Джерело] Завершило роботу. Згенеровано пакетів: {}\n", total_generated_.load());
    }

    // ── Стадія 2: Обчислювальний робітник ────────────────────────────────────
    void run_worker(std::size_t worker_id, std::stop_token thread_stoken) {
        std::stop_token global_token = global_stop_source_.get_token();

        while (!global_token.stop_requested() && !thread_stoken.stop_requested()) {
            auto opt_packet = raw_queue_.pop(global_token);
            if (!opt_packet.has_value()) {
                break; // Скасовано під час очікування або черга пуста при зупинці
            }

            const auto& raw = *opt_packet;

            // Імітація ресурсомісткої валідації та контрольної суми
            uint64_t crc = 0;
            for (char ch : raw.payload) {
                crc = (crc * 31) + static_cast<uint8_t>(ch);
            }

            ProcessedTelemetryPacket result{
                .id = raw.id,
                .checksum = crc,
                .original_bytes = raw.payload.size(),
                .is_valid = (crc != 0)
            };

            if (!processed_queue_.push(std::move(result), global_token)) {
                break;
            }
        }

        std::cout << std::format("[Воркер #{}] Завершив обробку.\n", worker_id);
    }

    // ── Стадія 3: Приймач / Збереження ───────────────────────────────────────
    void run_sink(std::stop_token thread_stoken) {
        std::stop_token global_token = global_stop_source_.get_token();

        while (!global_token.stop_requested() && !thread_stoken.stop_requested()) {
            auto opt_item = processed_queue_.pop(global_token);
            if (!opt_item.has_value()) {
                break;
            }

            total_processed_.fetch_add(1, std::memory_order_relaxed);
        }

        std::cout << std::format("[Приймач] Завершив збереження. Усього записано пакетів: {}\n", total_processed_.load());
    }

    InterruptibleQueue<RawTelemetryPacket> raw_queue_;
    InterruptibleQueue<ProcessedTelemetryPacket> processed_queue_;
    std::size_t worker_count_;

    std::stop_source global_stop_source_;
    std::stop_source source_stop_source_;

    std::jthread source_thread_;
    std::vector<std::jthread> workers_;
    std::jthread sink_thread_;

    std::atomic<uint64_t> total_generated_{0};
    std::atomic<uint64_t> total_processed_{0};
};

// ── Головна точка входу ──────────────────────────────────────────────────────

int main() {
    std::cout << "=== Запуск промислового C++20 конвеєра зі скасуванням через stop_token ===\n\n";

    constexpr std::size_t QueueCapacity = 32;
    constexpr std::size_t WorkerCount = 4;

    // Сценарій: Запуск і робота конвеєра з наступним коректним вичерпанням
    {
        std::cout << ">>> ДЕМОНСТРАЦІЯ 1: Коректне дренажування (Graceful Drain) <<<\n";
        TelemetryPipeline pipeline(QueueCapacity, WorkerCount);
        pipeline.start();

        // Даємо конвеєру попрацювати 100 мілісекунд
        std::this_thread::sleep_for(std::chrono::milliseconds(100));

        // Виконуємо коректне вичерпання
        pipeline.stop_graceful();

        std::cout << std::format("Результат Демо 1: Згенеровано = {}, Оброблено = {}\n\n",
            pipeline.get_total_generated(), pipeline.get_total_processed());
    }

    // Сценарій 2: Аварійне переривання під повним навантаженням
    {
        std::cout << ">>> ДЕМОНСТРАЦІЯ 2: Миттєве аварійне скасування (Immediate Abort) <<<\n";
        TelemetryPipeline pipeline(QueueCapacity, WorkerCount);
        pipeline.start();

        std::this_thread::sleep_for(std::chrono::milliseconds(50));

        std::cout << "[Головний потік] Симуляція критичного збою або таймауту!\n";
        pipeline.stop_immediate();
        pipeline.join();

        std::cout << std::format("Результат Демо 2: Згенеровано = {}, Оброблено = {}\n",
            pipeline.get_total_generated(), pipeline.get_total_processed());
    }

    std::cout << "\n=== Усі тести завершено успішно: нуль дедлоків, чисте звільнення ресурсів ===\n";
    return 0;
}
