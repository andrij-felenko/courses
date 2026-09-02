// Той самий стан без будь-якого захисту: фон і обробник переривання бʼються
// за одні комірки. Це вихідна вада, з якої починається стаття.
#include <cstdint>

#include "demo/demos.hpp"

namespace {

// STM32F4: TIM2 за адресою 0x40000000, регістр стану — зсув 0x10.
volatile std::uint32_t& tim2_sr = *reinterpret_cast<volatile std::uint32_t*>(0x40000010UL);
constexpr std::uint32_t kTimSrUif = 1U << 0;
constexpr std::uint32_t kFlagFrameReady = 1U << 3;

} // namespace

volatile std::uint32_t g_packet_counter{0};
volatile std::uint32_t g_device_flags{0};
volatile std::uint64_t g_timestamp_us{0}; // 64 біти на 32-бітному ядрі
volatile std::uint64_t g_isr_timestamp_seen{0};

namespace demo {

// Фоновий потік (Thread Mode).
void process_data() noexcept
{
    // Складене присвоєння для volatile у C++20 оголошено застарілим, тому
    // пишемо розгорнуто. Інструкцій це не міняє: LDR / ADDS / STR.
    g_packet_counter = g_packet_counter + 1;

    // Прапорець — те саме читання-зміна-запис, лише з ORR посередині.
    g_device_flags = g_device_flags | kFlagFrameReady;

    // 64-бітне число ядро пише двома інструкціями STR. Переривання між ними
    // лишає в памʼяті половину старого значення й половину нового.
    g_timestamp_us = g_timestamp_us + 50U;
}

std::uint32_t packet_counter() noexcept { return g_packet_counter; }

} // namespace demo

// Обробник переривання таймера (Handler Mode) — той самий стан.
extern "C" void TIM2_IRQHandler()
{
    tim2_sr = ~kTimSrUif; // зняти прапорець оновлення

    g_packet_counter = g_packet_counter + 1; // цей інкремент фон затре своїм STR
    g_isr_timestamp_seen = g_timestamp_us;   // а сюди може приїхати «гібрид»
}
