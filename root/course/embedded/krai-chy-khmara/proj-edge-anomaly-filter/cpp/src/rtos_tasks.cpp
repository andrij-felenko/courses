/*
 * Розділення роботи між двома пріоритетами RTOS.
 *
 * Задача давача крутиться на 100 Гц і не має права ні на мілісекунду
 * затримки: усе, що вона робить, — арифметика сталого часу й запис у чергу
 * без блокування. Задача зв'язку спить на порожній черзі й прокидається лише
 * тоді, коли є що везти; будити радіо з високопріоритетної задачі означало б
 * з'їсти вікно наступної вибірки на очікуванні ACK у сотні мілісекунд.
 */
#include <array>
#include <cstdint>
#include <limits>
#include <span>
#include <type_traits>

#include "FreeRTOS.h"
#include "queue.h"
#include "task.h"

#include "edge/anomaly_detector.hpp"
#include "edge/tasks.hpp"
#include "edge/telemetry_frame.hpp"

namespace edge {
namespace {

constexpr std::uint32_t sensor_period_ms = 10;   // 100 Гц
constexpr std::uint32_t adc_timeout_ms   = 5;
constexpr std::uint32_t ack_timeout_ms   = 2000;
constexpr std::uint32_t tx_attempts      = 3;
constexpr UBaseType_t   queue_length     = 8;
constexpr std::uint32_t sensor_stack_words = 256;
constexpr std::uint32_t comms_stack_words  = 512;

/// Одне повідомлення черги: звіт плюс уже розгорнута передісторія.
/// Кільце розгортає задача-джерело, бо детектор належить їй одній —
/// так задача зв'язку обходиться без м'ютекса й без доступу до його стану.
struct Message {
    Report                             report;
    std::array<float, snapshot_depth>  snapshot;
    std::uint8_t                       snapshot_len;
};

// FreeRTOS копіює повідомлення побайтово, тож тип мусить це витримувати.
static_assert(std::is_trivially_copyable_v<Message>);

/// Живлення радіокаскаду вимикається в БУДЬ-ЯКОМУ разі: забутий у
/// передавальному режимі PA з'їдає батарею за години. Ранній вихід із циклу
/// спроб, помилка кодування, майбутня зміна логіки — деструктор не забуде.
class RadioSession {
public:
    RadioSession() noexcept { radio_wake(); }
    ~RadioSession() noexcept { radio_sleep(); }

    RadioSession(const RadioSession&)            = delete;
    RadioSession& operator=(const RadioSession&) = delete;

    [[nodiscard]] bool transmit(std::span<const std::byte> frame) const noexcept
    {
        const auto* bytes = reinterpret_cast<const std::uint8_t*>(frame.data());
        for (std::uint32_t attempt = 0; attempt < tx_attempts; ++attempt) {
            if (radio_send(bytes, frame.size()) && radio_wait_ack(ack_timeout_ms)) {
                return true;
            }
        }
        return false;
    }
};

QueueHandle_t g_queue = nullptr;

StaticQueue_t g_queue_control;
std::array<std::uint8_t, queue_length * sizeof(Message)> g_queue_storage;

StaticTask_t g_sensor_tcb;
std::array<StackType_t, sensor_stack_words> g_sensor_stack;
StaticTask_t g_comms_tcb;
std::array<StackType_t, comms_stack_words> g_comms_stack;

volatile std::uint32_t g_dropped   = 0;
volatile std::uint32_t g_failed_tx = 0;

Millis now_ms() noexcept
{
    return Millis{static_cast<std::uint32_t>(xTaskGetTickCount() * portTICK_PERIOD_MS)};
}

void task_sensor(void*)
{
    TickType_t last_wake = xTaskGetTickCount();
    AnomalyDetector detector{now_ms()};

    for (;;) {
        vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(sensor_period_ms));

        float sample = 0.0f;
        if (!adc_read_sample(&sample, adc_timeout_ms)) {
            // Пропущене перетворення — не привід зупиняти цикл, але й тиші тут
            // бути не повинно: NaN піде звичайним шляхом і стане аварійним
            // звітом про відмову давача.
            sample = std::numeric_limits<float>::quiet_NaN();
        }

        const Report report = detector.process(sample, now_ms());
        if (report.action == Action::Discard) {
            continue;   // найчастіша гілка: назад у сон
        }

        Message msg{};
        msg.report = report;
        msg.snapshot_len =
            static_cast<std::uint8_t>(detector.snapshot(std::span{msg.snapshot}));

        // Нуль замість очікування: високопріоритетна задача НЕ блокується на
        // черзі. Якщо радіо не встигає — втрачаємо звіт і рахуємо втрату,
        // але темп опитування давача не зриваємо.
        if (xQueueSendToBack(g_queue, &msg, 0) != pdPASS) {
            ++g_dropped;
        }
    }
}

void task_comms(void*)
{
    static FrameStorage frame;   // 88 байт: у BSS, а не на стеку задачі
    Message msg{};

    for (;;) {
        if (xQueueReceive(g_queue, &msg, portMAX_DELAY) != pdPASS) {
            continue;
        }

        const std::span<const float> history{msg.snapshot.data(), msg.snapshot_len};
        const auto encoded = encode(msg.report, history, std::span{frame});
        if (!encoded) {
            ++g_failed_tx;   // кадр не вліз — везти нема чого
            continue;
        }

        const RadioSession radio;
        if (!radio.transmit(*encoded)) {
            ++g_failed_tx;
        }
    }
}

}  // namespace

std::uint32_t dropped_reports() noexcept      { return g_dropped; }
std::uint32_t failed_transmissions() noexcept { return g_failed_tx; }

bool telemetry_start()
{
    g_queue = xQueueCreateStatic(queue_length,
                                 sizeof(Message),
                                 g_queue_storage.data(),
                                 &g_queue_control);
    if (g_queue == nullptr) {
        return false;
    }

    const TaskHandle_t sensor =
        xTaskCreateStatic(task_sensor, "sensor", sensor_stack_words, nullptr,
                          configMAX_PRIORITIES - 2, g_sensor_stack.data(), &g_sensor_tcb);
    const TaskHandle_t comms =
        xTaskCreateStatic(task_comms, "comms", comms_stack_words, nullptr,
                          tskIDLE_PRIORITY + 1, g_comms_stack.data(), &g_comms_tcb);

    return sensor != nullptr && comms != nullptr;
}

}  // namespace edge
