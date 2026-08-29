// ===========================================================================
//  calibration_task.cpp — інтеграція конвеєра у FreeRTOS
//
//  Два завдання з різними пріоритетами:
//    · сенсорне (100 Гц, високий пріоритет) — читає магнітометр і гіроскоп,
//      коригує вимір чинними коефіцієнтами й віддає його оцінювачу;
//    · калібрувальне (10 Гц, низький пріоритет) — тайм-аути, телеметрія і
//      сам розв'язувач, який рахує 2–4 мс і тому не сміє виконуватись у
//      часі, вкраденому в контуру стабілізації.
//
//  М'ютекс накриває сесію, але НЕ розв'язувач: той дістає копію хмари,
//  зняту за десяток мікросекунд, і далі мовчки рахує свою математику.
// ===========================================================================

#include <atomic>
#include <optional>

#include "FreeRTOS.h"
#include "semphr.h"
#include "task.h"
#include "mag_cal/session.hpp"
#include "mag_cal/solver.hpp"

namespace mag_cal::app {

// Порт плати: драйвери й годинник
namespace board {
[[nodiscard]] std::uint32_t millis() noexcept;
[[nodiscard]] std::optional<Vec3> read_mag_ut() noexcept;    // RM3100 / IST8310
[[nodiscard]] std::optional<Vec3> read_gyro_rad_s() noexcept;
void publish_mag(const Vec3& calibrated) noexcept;           // вхід оцінювача
}  // namespace board

namespace {

constexpr TickType_t kSensorPeriod = pdMS_TO_TICKS(10);    // 100 Гц
constexpr TickType_t kWorkerPeriod = pdMS_TO_TICKS(100);   // 10 Гц
constexpr TickType_t kSensorLockWait = pdMS_TO_TICKS(2);
constexpr TickType_t kArmingLockWait = pdMS_TO_TICKS(5);
constexpr std::size_t kSensorStackWords = 512;
constexpr std::size_t kWorkerStackWords = 1024;   // розв'язувачу треба H[9][9]

// Уся пам'ять статична: динамічного розподілу в польотному контурі немає
StaticTask_t g_sensor_tcb;
StackType_t g_sensor_stack[kSensorStackWords];
StaticTask_t g_worker_tcb;
StackType_t g_worker_stack[kWorkerStackWords];
StaticSemaphore_t g_mutex_storage;
SemaphoreHandle_t g_mutex = nullptr;

// Сесія має нетривіальний конструктор, тому створюється явно у start(),
// а не порядком ініціалізації статичних об'єктів.
std::optional<CalibrationSession> g_session;
Collector g_snapshot;   // ~3.5 КБ; належить робочому завданню

// Заявки з обробника команд MAVLink (MAV_CMD_DO_START_MAG_CAL і скасування):
// команда приходить із чужого потоку, тому прапорці, а не прямий виклик.
std::atomic<bool> g_start_requested{false};
std::atomic<bool> g_cancel_requested{false};

// М'ютекс під RAII: жодна гілка виходу не забуде його віддати
class ScopedLock {
public:
    explicit ScopedLock(SemaphoreHandle_t handle,
                        TickType_t wait = portMAX_DELAY) noexcept
        : handle_{handle}, held_{xSemaphoreTake(handle, wait) == pdTRUE} {}

    ~ScopedLock() {
        if (held_) {
            xSemaphoreGive(handle_);
        }
    }

    ScopedLock(const ScopedLock&) = delete;
    ScopedLock& operator=(const ScopedLock&) = delete;
    ScopedLock(ScopedLock&&) = delete;
    ScopedLock& operator=(ScopedLock&&) = delete;

    [[nodiscard]] explicit operator bool() const noexcept { return held_; }

private:
    SemaphoreHandle_t handle_;
    bool held_;
};

void sensor_task(void* /*arg*/) {
    TickType_t last_wake = xTaskGetTickCount();

    for (;;) {
        vTaskDelayUntil(&last_wake, kSensorPeriod);

        const auto raw = board::read_mag_ut();
        const auto gyro = board::read_gyro_rad_s();
        if (!raw || !gyro) {
            continue;   // збій шини: пропускаємо такт мовчки
        }

        const std::uint32_t now = board::millis();
        Vec3 calibrated = *raw;

        {
            // Тримаємо м'ютекс рівно стільки, скільки треба на застосування
            // коефіцієнтів і запис однієї точки в комірку.
            const ScopedLock lock{g_mutex, kSensorLockWait};
            if (lock) {
                calibrated = g_session->correct(*raw);
                static_cast<void>(g_session->push(*raw, *gyro, now));
            }
        }

        board::publish_mag(calibrated);
    }
}

void worker_task(void* /*arg*/) {
    TickType_t last_wake = xTaskGetTickCount();

    {
        // Старт плати: піднімаємо коефіцієнти з Flash і звіряємо CRC32
        const ScopedLock lock{g_mutex};
        static_cast<void>(g_session->boot(board::millis()));
    }

    for (;;) {
        vTaskDelayUntil(&last_wake, kWorkerPeriod);

        const std::uint32_t now = board::millis();
        bool need_solve = false;

        {
            const ScopedLock lock{g_mutex};
            if (!lock) {
                continue;
            }

            if (g_start_requested.exchange(false)) {
                static_cast<void>(g_session->start(now));
            }
            if (g_cancel_requested.exchange(false)) {
                g_session->cancel(now);
            }

            g_session->service(now);

            if (g_session->ready_to_solve()) {
                g_session->begin_solve(now);
                g_snapshot = g_session->collector();   // копія хмари, ~10 мкс
                need_solve = true;
            }
        }

        if (!need_solve) {
            continue;
        }

        // Найдорожча частина циклу — і вона поза м'ютексом
        const auto outcome = fit_ellipsoid(g_snapshot.samples(), g_snapshot.earth_field(),
                                           g_snapshot.coverage_percent());

        const ScopedLock lock{g_mutex};
        if (lock) {
            g_session->submit(outcome, board::millis());
        }
    }
}

}  // namespace

void request_start() noexcept {
    g_start_requested.store(true);
}

void request_cancel() noexcept {
    g_cancel_requested.store(true);
}

// Знімок для гейта озброєння: м'ютекс зайнятий довше за 5 мс — не злітаємо
[[nodiscard]] bool arming_allowed() noexcept {
    const ScopedLock lock{g_mutex, kArmingLockWait};
    return lock && g_session && g_session->arming_allowed();
}

void start(std::uint8_t system_id, std::uint8_t component_id, std::uint8_t compass_id,
           float earth_field_ut) {
    g_mutex = xSemaphoreCreateMutexStatic(&g_mutex_storage);
    configASSERT(g_mutex != nullptr);

    g_session.emplace(system_id, component_id, compass_id, earth_field_ut);

    static_cast<void>(xTaskCreateStatic(sensor_task, "mag_sensor", kSensorStackWords,
                                        nullptr, configMAX_PRIORITIES - 2,
                                        g_sensor_stack, &g_sensor_tcb));

    static_cast<void>(xTaskCreateStatic(worker_task, "mag_cal", kWorkerStackWords,
                                        nullptr, tskIDLE_PRIORITY + 1, g_worker_stack,
                                        &g_worker_tcb));
}

}  // namespace mag_cal::app
