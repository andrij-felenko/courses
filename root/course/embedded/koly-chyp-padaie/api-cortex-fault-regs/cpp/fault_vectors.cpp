// fault_vectors.cpp — «голі» вектори винятків збою.
//
// Обробник не має права бути звичайною функцією: пролог компілятора зіпсує LR
// (там лежить EXC_RETURN) і зрушить стек до того, як ми знімемо кадр аварії.
// Тому кожен вектор — три інструкції: вибрати стек за бітом 2 у EXC_RETURN,
// передати кадр і LR далі.
//
// Хвостовий перехід (b), а не виклик (bl): fault_entry не повертається,
// і зайвий кадр на й так підозрілому стеку нам не потрібен.
#include "fault_report.hpp"

extern "C" {

[[gnu::naked]] void HardFault_Handler()
{
    asm volatile(
        ".syntax unified   \n"
        "tst   lr, #4      \n"   // біт 2 EXC_RETURN
        "ite   eq          \n"
        "mrseq r0, msp     \n"   // 0 → кадр на головному стеку
        "mrsne r0, psp     \n"   // 1 → кадр на стеку задачі
        "mov   r1, lr      \n"
        "mov   r2, #0      \n"   // Source::hard
        "b     fault_entry \n");
}

[[gnu::naked]] void MemManage_Handler()
{
    asm volatile(
        ".syntax unified   \n"
        "tst   lr, #4      \n"
        "ite   eq          \n"
        "mrseq r0, msp     \n"
        "mrsne r0, psp     \n"
        "mov   r1, lr      \n"
        "mov   r2, #1      \n"   // Source::mem_manage
        "b     fault_entry \n");
}

[[gnu::naked]] void BusFault_Handler()
{
    asm volatile(
        ".syntax unified   \n"
        "tst   lr, #4      \n"
        "ite   eq          \n"
        "mrseq r0, msp     \n"
        "mrsne r0, psp     \n"
        "mov   r1, lr      \n"
        "mov   r2, #2      \n"   // Source::bus
        "b     fault_entry \n");
}

[[gnu::naked]] void UsageFault_Handler()
{
    asm volatile(
        ".syntax unified   \n"
        "tst   lr, #4      \n"
        "ite   eq          \n"
        "mrseq r0, msp     \n"
        "mrsne r0, psp     \n"
        "mov   r1, lr      \n"
        "mov   r2, #3      \n"   // Source::usage
        "b     fault_entry \n");
}

// Точка стику асемблера з типізованим кодом: далі працюють уже посилання
// й enum class, а не сирі слова.
[[noreturn]] void fault_entry(const fault::ExceptionFrame* frame,
                              std::uint32_t exc_return,
                              std::uint32_t source)
{
    fault::report(*frame, fault::ExcReturn{exc_return}, static_cast<fault::Source>(source));
}

}  // extern "C"
