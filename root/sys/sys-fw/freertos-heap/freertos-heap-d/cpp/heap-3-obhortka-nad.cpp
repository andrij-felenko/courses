#include <memory>
#include <concepts>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

namespace rtos::heap3 {

template <typename T, typename... Args>
[[nodiscard]] std::unique_ptr<T, void(*)(T*)> make_unique_task_safe(Args&&... args)
{
    vTaskSuspendAll();
    void* raw_mem = std::malloc(sizeof(T));
    xTaskResumeAll();

    if (!raw_mem) {
        return {nullptr, [](T*){}};
    }

    T* object = ::new (raw_mem) T(std::forward<Args>(args)...);

    return {
        object,
        [](T* ptr) noexcept {
            if (ptr) {
                ptr->~T();
                vTaskSuspendAll();
                std::free(static_cast<void*>(ptr));
                xTaskResumeAll();
            }
        }
    };
}

} // namespace rtos::heap3
