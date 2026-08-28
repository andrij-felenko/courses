#include <string.h>
#include <stddef.h>   // offsetof — зсув поля в структурі
#include "timer.h"    // ваш драйвер: timer_now_us() — вільний лічильник у мкс

// Пакет, що ходить по дроту. На чипі його розкладання МУСИТЬ бути точним:
// 1 + 4 + 2 = 7 байтів БЕЗ доповнення, бо поля впорядковані й спаковані.
struct __attribute__((packed)) telemetry {
    uint8_t  id;         // зсув 0
    uint32_t timestamp;  // зсув 1
    uint16_t voltage;    // зсув 5
};                       // sizeof МАЄ бути 7

static void test_packet_layout(void) {
    // На x86-64 без packed це було б 12 байтів (вирівнювання uint32_t на 4).
    // На живому Cortex-M із packed — рівно 7. Оце й перевіряємо ТУТ, а не на хості.
    expect(sizeof(struct telemetry) == 7, "sizeof(telemetry)==7");
    expect(offsetof(struct telemetry, timestamp) == 1, "offset(timestamp)==1");
    expect(offsetof(struct telemetry, voltage)   == 5, "offset(voltage)==5");
}

static void test_timer_real_ticks(void) {
    // Реальний тайминг: заміряти, скільки мкс мине за ~1000 порожніх ітерацій.
    // На хості це безглуздо (інша частота, інший код); на живому чипі — правда.
    uint32_t t0 = timer_now_us();
    for (volatile int i = 0; i < 1000; i++) { /* палимо такти навмисне */ }
    uint32_t dt = timer_now_us() - t0;
    // Знаючи частоту ядра, ми очікуємо цикл у відомому вікні. Порожні межі —
    // приклад; справжні беруться з даташита й заміру. Головне: це РЕАЛЬНІ такти.
    expect(dt > 5 && dt < 5000, "порожній цикл у розумному вікні мкс");
}
