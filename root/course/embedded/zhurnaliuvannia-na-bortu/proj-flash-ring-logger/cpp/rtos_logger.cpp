#include "rtos_logger.hpp"

#include <mutex>

namespace fl {
namespace {

constexpr configSTACK_DEPTH_TYPE kDrainStackWords = 512;
constexpr TickType_t kDrainIdlePeriodMs = 500;

}  // namespace

bool RtosLogger::start()
{
    // М'ютекс саме рекурсивний: службовий запис про дефектний сектор
    // народжується всередині RingLogger::append(), тобто вже під захопленим
    // замком. Зі звичайним м'ютексом задача заклинила б сама на собі.
    if (!mutex_.valid()) {
        return false;
    }

    // Найнижчий пріоритет над бездіяльною задачею: журнал не має права
    // відбирати такти в керування.
    return xTaskCreate(&RtosLogger::taskEntry, "logdrain", kDrainStackWords, this,
                       tskIDLE_PRIORITY + 1, &task_) == pdPASS;
}

void RtosLogger::taskEntry(void* argument)
{
    static_cast<RtosLogger*>(argument)->drainLoop();
}

void RtosLogger::drainLoop()
{
    for (;;) {
        // Прокидаємося або від сповіщення з переривання, або раз на пів
        // секунди — друге потрібне, щоб не проґавити кадр, покладений у чергу
        // рівно тоді, коли задача вже виходила з очікування.
        static_cast<void>(ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(kDrainIdlePeriodMs)));

        const std::lock_guard guard{mutex_};
        static_cast<void>(drain(stage_, core_));
    }
}

std::expected<void, LoggerError> RtosLogger::log(Level level, std::uint8_t moduleId,
                                                 std::uint32_t tokenId,
                                                 std::span<const std::byte> payload)
{
    const auto nowMs = static_cast<std::uint32_t>(xTaskGetTickCount() * portTICK_PERIOD_MS);

    const std::lock_guard guard{mutex_};
    return core_.append(level, moduleId, nowMs, tokenId, payload);
}

void RtosLogger::logFromIsr(Level level, std::uint8_t moduleId, std::uint32_t tokenId,
                            std::uint16_t arg) noexcept
{
    const StagedRecord record{
        .level = level,
        .moduleId = moduleId,
        .arg = arg,
        .timestampMs = static_cast<std::uint32_t>(xTaskGetTickCountFromISR() * portTICK_PERIOD_MS),
        .tokenId = tokenId,
    };

    // Черга повна — кадр гине, і це правильно: тримати переривання заради
    // журналу не можна. Утрату порахує сама черга.
    static_cast<void>(stage_.push(record));

    BaseType_t higherPriorityTaskWoken = pdFALSE;
    vTaskNotifyGiveFromISR(task_, &higherPriorityTaskWoken);
    portYIELD_FROM_ISR(higherPriorityTaskWoken);
}

std::expected<Batch, LoggerError> RtosLogger::readBatch(std::span<std::byte> buffer)
{
    const std::lock_guard guard{mutex_};
    return core_.readBatch(buffer);
}

std::expected<void, LoggerError> RtosLogger::commitTail(std::uint32_t sectorIdx)
{
    const std::lock_guard guard{mutex_};
    return core_.commitTail(sectorIdx);
}

}  // namespace fl
