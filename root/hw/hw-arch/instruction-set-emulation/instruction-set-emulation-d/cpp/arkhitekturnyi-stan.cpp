#include <cstdint>
#include <array>

constexpr size_t GuestRegsCount = 32;

struct CPUState {
    std::array<uint32_t, GuestRegsCount> regs{}; // Регістри загального призначення
    uint32_t pc{0};                              // Гостьовий лічильник команд
    uint32_t sp{0};                              // Вказівник стека
    
    // Поля лінивого обчислення прапорців стану
    uint32_t cc_op{0};                           // Код останньої операції
    uint32_t cc_src1{0};                         // Перший вхідний операнд
    uint32_t cc_src2{0};                         // Другий вхідний операнд
    uint32_t cc_dst{0};                          // Результат операції
    
    // Бюджет інструкцій для таймерів та переривань
    int32_t  icount_budget{0};
    
    bool     halted{false};                      // Прапорець зупинки
    uint32_t pending_interrupts{0};              // Бітова маска переривань
};
