#include <iostream>
#include <string>
#include <memory>
#include <mutex>
#include <atomic>
#include <random>
#include <future>
#include <chrono>
#include <stdexcept>

// Стан пристрою в системі Digital Home
struct DeviceState {
    std::string device_id;
    int target_temperature;
    bool is_active;
};

// Шов (seam): чистий доменний контракт взаємодії
class IDeviceAutomation {
public:
    virtual ~IDeviceAutomation() = default;
    virtual DeviceState UpdateState(const std::string& id, int temp, bool active) = 0;
};

// 1. Локальна реалізація для модульного моноліту (спільна пам'ять, нульові копіювання)
class LocalDeviceAutomation : public IDeviceAutomation {
private:
    std::mutex state_lock_;
    DeviceState state_;

public:
    LocalDeviceAutomation() : state_{"thermostat-zone-1", 20, true} {}

    DeviceState UpdateState(const std::string& id, int temp, bool active) override {
        // Локальна атомарна транзакція в пам'яті під м'ютексом
        std::lock_guard<std::mutex> guard(state_lock_);
        state_.device_id = id;
        state_.target_temperature = temp;
        state_.is_active = active;
        // Затримка на рівні наносекунд: немає серіалізації та системних викликів
        return state_;
    }
};

// 2. Віддалений клієнтський адаптер через межу мережі (RPC, потрійний податок)
class RemoteDeviceAdapter : public IDeviceAutomation {
public:
    DeviceState UpdateState(const std::string& id, int temp, bool active) override {
        // Симуляція мережевого RPC: серіалізація в DTO, передача по сокету
        std::this_thread::sleep_for(std::chrono::milliseconds(15));

        // Симуляція випадкового мережевого збою для перевірки відмовостійкості
        static std::atomic<int> counter{0};
        if (++counter % 50 == 0) {
            throw std::runtime_error("Мережевий таймаут перетину межі RPC");
        }

        return DeviceState{id, temp, active};
    }
};

// Режими життєвого циклу архітектурної межі
enum class BoundaryMode {
    DirectLocal,     // Модульний моноліт: прямий локальний виклик
    DualRunShadow,   // Тіньовий запуск: локальний повертає, віддалений перевіряється у фоні
    CanaryRemote,    // Канарка: відсоток трафіку йде у віддалений сервіс із локальним резервом
    DirectRemote     // Повне розрізання: 100% трафіку йде через мережеву межу
};

// 3. Еволюційний диспетчер: керує перекроюванням межі без зупинки системи
class EvolutionaryBoundaryDispatcher : public IDeviceAutomation {
private:
    std::shared_ptr<IDeviceAutomation> local_;
    std::shared_ptr<IDeviceAutomation> remote_;
    std::atomic<BoundaryMode> mode_;
    std::atomic<uint32_t> canary_percentage_; // 0..100%

public:
    EvolutionaryBoundaryDispatcher(
        std::shared_ptr<IDeviceAutomation> local_impl,
        std::shared_ptr<IDeviceAutomation> remote_impl
    ) : local_(std::move(local_impl)),
        remote_(std::move(remote_impl)),
        mode_(BoundaryMode::DirectLocal),
        canary_percentage_(0) {}

    void SetMode(BoundaryMode new_mode, uint32_t canary_pct = 0) {
        canary_percentage_.store(canary_pct);
        mode_.store(new_mode);
    }

    DeviceState UpdateState(const std::string& id, int temp, bool active) override {
        BoundaryMode current_mode = mode_.load();

        switch (current_mode) {
            case BoundaryMode::DirectLocal:
                // Режим моноліту: мінімальна затримка, максимальна надійність
                return local_->UpdateState(id, temp, active);

            case BoundaryMode::DualRunShadow: {
                // Виконуємо локально — це гарантована відповідь користувачу
                DeviceState local_result = local_->UpdateState(id, temp, active);

                // Тіньове асинхронне виконання віддаленого виклику для звірки контрактів
                std::async(std::launch::async, [this, id, temp, active, local_result]() {
                    try {
                        DeviceState remote_result = remote_->UpdateState(id, temp, active);
                        if (remote_result.target_temperature != local_result.target_temperature) {
                            std::cerr << "[Тіньова розбіжність] Несумісність стану для " << id << "\n";
                        }
                    } catch (const std::exception& ex) {
                        std::cerr << "[Тіньова помилка віддаленої межі] " << ex.what() << "\n";
                    }
                });

                return local_result;
            }

            case BoundaryMode::CanaryRemote: {
                // Визначаємо, чи запит потрапляє у відсоток канарки
                static thread_local std::mt19937 gen(std::random_device{}());
                std::uniform_int_distribution<uint32_t> dist(1, 100);

                if (dist(gen) <= canary_percentage_.load()) {
                    try {
                        // Спроба відправити на нову віддалену межу
                        return remote_->UpdateState(id, temp, active);
                    } catch (const std::exception& ex) {
                        // Аварійне повернення на перевірену локальну реалізацію
                        std::cerr << "[Канарковий збій -> Відкат до локального] " << ex.what() << "\n";
                        return local_->UpdateState(id, temp, active);
                    }
                }
                return local_->UpdateState(id, temp, active);
            }

            case BoundaryMode::DirectRemote:
                // Сервіс повністю відокремлено за новою межею
                return remote_->UpdateState(id, temp, active);
        }

        return local_->UpdateState(id, temp, active);
    }
};
