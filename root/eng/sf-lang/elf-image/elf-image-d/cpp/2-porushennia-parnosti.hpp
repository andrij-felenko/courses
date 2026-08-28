#include <cstdint>

namespace boot {

using AppEntryPoint = void (*)();

inline void jump_to_application(std::uint32_t app_vector_table_addr) noexcept {
    const auto* vector_table = reinterpret_cast<const volatile std::uint32_t*>(app_vector_table_addr);
    const auto reset_handler_addr = vector_table[1]; // Вектор Reset_Handler

    // Адреса в таблиці векторів уже містить Thumb-біт (біт 0 = 1)
    const auto app_entry = reinterpret_cast<AppEntryPoint>(reset_handler_addr);
    app_entry();
}

} // namespace boot
