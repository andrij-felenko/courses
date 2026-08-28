#include <iostream>
#include <cstdint>
#include <concepts>

/* Опис трейт-контракту */
template <typename TraitVTable>
struct DynRef {
    const void* data_ptr{nullptr};
    const TraitVTable* vtable_ptr{nullptr};
};

struct LoggerVTable {
    void (*log_msg)(const void* data) noexcept;
};

/* Чистий тип без спадкування та без vptr */
struct TemperatureSensor {
    int32_t celsius{0};
    uint32_t sensor_id{0};
};

/* Будівник жирного покажчика для типу TemperatureSensor */
class LoggerTrait {
public:
    template <typename T>
    [[nodiscard]] static DynRef<LoggerVTable> create(const T& obj) noexcept {
        static constexpr LoggerVTable vtbl{
            .log_msg = [](const void* data) noexcept {
                const auto* val = static_cast<const T*>(data);
                (void)val;
            }
        };

        return DynRef<LoggerVTable>{
            .data_ptr = &obj,
            .vtable_ptr = &vtbl
        };
    }
};

/* Функція, що приймає знеособлений жирний покажчик */
void execute_log(DynRef<LoggerVTable> dyn) noexcept {
    dyn.vtable_ptr->log_msg(dyn.data_ptr);
}
