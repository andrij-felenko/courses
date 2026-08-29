// reset.cpp — векторна таблиця, точка входу Reset_Handler і налаштування ядра.
//
// Таблиця й обробники лежать в одному модулі трансляції навмисно: слабкі
// псевдоніми мусять посилатися на ціль із того самого об'єктного файла.
//
// ⚠ Код цього файла виконується ДО того, як RAM набула коректного стану. Тому
// Reset_Handler і все, що він кличе до виклику configure_core(), не має права
// торкатися глобальних змінних: .data ще у Flash, .bss заповнена сміттям після
// подачі живлення. Дозволено лише локальні змінні на стеку й символи лінкера.

#include <cstdint>

#include "mcu/linker_symbols.hpp"
#include "mcu/scb.hpp"

// Ім'я main не мангліфікується за жодних умов, тож обгортка extern "C" йому не
// потрібна (а деякі компілятори її на ::main і не дозволяють).
int main();

extern "C" {

// ── 1. Обробники, які прошивка може перевизначити ────────────────────────────
// Кожен — слабкий псевдонім Default_Handler. Щойно десь з'явиться звичайна
// функція з таким самим іменем, лінкер підставить у таблицю саме її. Імена
// мусять бути в extern "C": alias працює з символом, а не з іменем C++.

[[noreturn]] void Default_Handler();
[[noreturn]] void Reset_Handler();

void NMI_Handler()        __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler()  __attribute__((weak, alias("Default_Handler")));
void MemManage_Handler()  __attribute__((weak, alias("Default_Handler")));
void BusFault_Handler()   __attribute__((weak, alias("Default_Handler")));
void UsageFault_Handler() __attribute__((weak, alias("Default_Handler")));
void SVC_Handler()        __attribute__((weak, alias("Default_Handler")));
void DebugMon_Handler()   __attribute__((weak, alias("Default_Handler")));
void PendSV_Handler()     __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler()    __attribute__((weak, alias("Default_Handler")));

}  // extern "C"

using Handler = void (*)();

// Перше слово таблиці — не обробник, а початкове значення покажчика стека.
// Тому воно оголошене як void*, а не як Handler: reinterpret_cast заборонений
// у сталих виразах, і таблиця з ним поїхала б у динамічну ініціалізацію —
// тобто не існувала б на момент, коли ядро її читає. Через void* адреса
// лишається адресною сталою, і таблиця потрапляє у Flash готовою.
//
// Тип оголошено на рівні файла, а не в безіменному просторі імен: у самої
// таблиці зовнішнє зв'язування (extern "C"), і тип із внутрішнім зв'язуванням
// у її оголошенні був би несумісною сумішшю.
struct VectorTable {
    void* initial_stack_pointer;
    Handler handlers[15];
};

// Атрибут used забороняє викинути таблицю, на яку ніхто не посилається з коду,
// а KEEP у скрипті лінкера — вирізати секцію при --gc-sections.
// Перші 16 записів задані архітектурою; вектори периферії конкретного чипа
// дописуються далі за тим самим зразком.
extern "C" __attribute__((section(".isr_vector"), used))
const VectorTable g_vector_table = {
    &_estack,               // 0x00: початкова вершина стека MSP
    {
        Reset_Handler,      // 0x04: точка входу після скидання
        NMI_Handler,        // 0x08: немасковане переривання
        HardFault_Handler,  // 0x0C: фатальний збій
        MemManage_Handler,  // 0x10: порушення захисту MPU
        BusFault_Handler,   // 0x14: помилка шини
        UsageFault_Handler, // 0x18: невірна інструкція, ділення на нуль
        nullptr, nullptr, nullptr, nullptr,  // 0x1C..0x28: зарезервовано ARM
        SVC_Handler,        // 0x2C: системний виклик
        DebugMon_Handler,   // 0x30: монітор налагодження
        nullptr,            // 0x34: зарезервовано ARM
        PendSV_Handler,     // 0x38: відкладений виклик RTOS
        SysTick_Handler,    // 0x3C: системний таймер
    },
};

namespace {

// Копіювання й занулення пишуться явними циклами, а не std::ranges::copy і
// std::ranges::fill: будь-який із них компілятор має право згорнути у виклик
// memcpy чи memset, а це стрибок у бібліотеку раніше, ніж її дані існують.
// Атрибут вимикає рівно цю оптимізацію, тож модуль лишається цілим незалежно
// від прапорців збірки.
__attribute__((optimize("no-tree-loop-distribute-patterns")))
void initialize_data_and_bss() noexcept
{
    auto data = mcu::linker::data_section();
    const auto image = mcu::linker::data_image();
    for (std::size_t i = 0; i < data.size(); ++i) {
        data[i] = image[i];
    }

    auto bss = mcu::linker::bss_section();
    for (std::size_t i = 0; i < bss.size(); ++i) {
        bss[i] = 0;
    }
}

// Увімкнення співпроцесора з рухомою комою (Cortex-M4F / M7 / M33). Після
// скидання CP10 і CP11 апаратно вимкнені задля енергозбереження: перша ж
// інструкція vldr при вимкненому FPU дає UsageFault з ознакою NOCP.
void enable_fpu() noexcept
{
    mcu::cpacr::set(mcu::bits::cp10_cp11_full);
    // dsb доводить запис до кінця, isb очищує конвеєр: наступні інструкції з
    // рухомою комою декодуються вже увімкненим співпроцесором.
    mcu::dsb();
    mcu::isb();
}

// Базове налаштування ядра. Тактування тут навмисно не чіпається: PLL,
// дільники й затримки Flash у кожного чипа свої, а стартовий код від чипа не
// залежить.
void configure_core() noexcept
{
    // Векторна таблиця. Прошивка, залита з початку Flash, працює й без цього
    // запису, — але щойно образ переїде за завантажувач, VTOR стає обов'язковим.
    mcu::vtor::store(reinterpret_cast<std::uint32_t>(&g_vector_table));

    // Власні вектори для MemManage, BusFault і UsageFault. Без цих бітів ядро
    // ескалює будь-який із них у HardFault, і причину доводиться відновлювати
    // за ознакою FORCED.
    mcu::shcsr::set(mcu::bits::memfault_enable |
                    mcu::bits::busfault_enable |
                    mcu::bits::usgfault_enable);

    // Пастка на ділення цілого на нуль: без неї udiv тихо віддає нуль, і
    // помилка спливає за десять кроків від місця, де сталася.
    mcu::ccr::set(mcu::bits::div_0_trap);

    mcu::dsb();
    mcu::isb();
}

// Конструктори глобальних об'єктів. .preinit_array виконується першим — так
// вимагає стандарт; порожній покажчик у таблиці пропускаємо.
void run_static_constructors() noexcept
{
    for (auto initializer : mcu::linker::preinit_array()) {
        if (initializer != nullptr) { initializer(); }
    }
    for (auto initializer : mcu::linker::init_array()) {
        if (initializer != nullptr) { initializer(); }
    }
}

}  // namespace

extern "C" [[noreturn]] __attribute__((used)) void Reset_Handler()
{
    initialize_data_and_bss();
    // Від цього рядка глобальні змінні мають коректні значення.

    enable_fpu();
    configure_core();
    run_static_constructors();

    main();

    // Повертатися main() нема куди: операційної системи не існує, а за кінцем
    // стартового коду лежать чужі байти.
    mcu::halt();
}

// Вектор, який прошивка не перевизначила. Порожній вічний цикл приховав би
// причину: під налагоджувачем видно лише «десь крутиться». halt() спиняє ядро
// точкою зупину, а номер винятку лишається в ICSR.
extern "C" [[noreturn]] void Default_Handler()
{
    mcu::halt();
}
