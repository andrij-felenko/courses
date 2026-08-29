// Прив'язка журналу до FreeRTOS: рекурсивний м'ютекс на шину й фонова задача,
// що переносить кадри з черги переривань у Flash.
//
// Модуль збирається лише під ціль — на хості FreeRTOS немає, тож
// recovery_demo.cpp працює з RingLogger напряму.

#pragma once

#include "FreeRTOS.h"
#include "semphr.h"
#include "task.h"

#include "ring_logger.hpp"
#include "staging_ring.hpp"

namespace fl {

// Обгортка з інтерфейсом BasicLockable — з нею працює звичайний
// std::lock_guard, і жодна гілка виходу не забуде віддати м'ютекс.
class RecursiveMutex {
public:
    RecursiveMutex() : handle_{xSemaphoreCreateRecursiveMutex()} {}

    ~RecursiveMutex()
    {
        if (handle_ != nullptr) {
            vSemaphoreDelete(handle_);
        }
    }

    RecursiveMutex(const RecursiveMutex&) = delete;
    RecursiveMutex& operator=(const RecursiveMutex&) = delete;

    [[nodiscard]] bool valid() const noexcept { return handle_ != nullptr; }

    void lock() { static_cast<void>(xSemaphoreTakeRecursive(handle_, portMAX_DELAY)); }
    void unlock() { static_cast<void>(xSemaphoreGiveRecursive(handle_)); }

private:
    SemaphoreHandle_t handle_{nullptr};
};

class RtosLogger {
public:
    RtosLogger(RingLogger& core, StagingRing<kStageCapacity>& stage) noexcept
        : core_{core}, stage_{stage} {}

    RtosLogger(const RtosLogger&) = delete;
    RtosLogger& operator=(const RtosLogger&) = delete;

    // Створює фонову задачу. Ядро вже має бути ініціалізоване RingLogger::init().
    bool start();

    // Запис зі звичайної задачі: мітку часу бере з тіків планувальника.
    std::expected<void, LoggerError> log(Level level, std::uint8_t moduleId, std::uint32_t tokenId,
                                         std::span<const std::byte> payload = {});

    // Запис із переривання: лише кладе кадр у чергу й будить фонову задачу.
    void logFromIsr(Level level, std::uint8_t moduleId, std::uint32_t tokenId,
                    std::uint16_t arg) noexcept;

    // Вивантаження під тим самим м'ютексом — шина в модема й у журналу спільна.
    std::expected<Batch, LoggerError> readBatch(std::span<std::byte> buffer);
    std::expected<void, LoggerError> commitTail(std::uint32_t sectorIdx);

private:
    static void taskEntry(void* argument);
    [[noreturn]] void drainLoop();

    RingLogger& core_;
    StagingRing<kStageCapacity>& stage_;
    RecursiveMutex mutex_{};
    TaskHandle_t task_{nullptr};
};

}  // namespace fl
