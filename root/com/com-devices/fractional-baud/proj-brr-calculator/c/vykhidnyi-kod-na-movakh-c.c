#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Результати розрахунку конфігурації дільника для STM32 */
typedef struct {
    uint32_t f_ck;          /* Тактова частота шини периферії APB (Гц) */
    uint32_t target_baud;   /* Цільова швидкість передачі (бод) */
    uint32_t real_baud;     /* Фактично отримана швидкість (бод) */
    double error_percent;   /* Відносна похибка встановлення швидкості (%) */
    uint16_t brr_value;     /* 16-бітне значення для запису в USART_BRR */
    uint16_t mantissa;      /* Мантиса (ціла частина коефіцієнта N) */
    uint8_t fraction;       /* Дробова частина (чисельник F) */
    bool over8;             /* Прапорець режиму OVER8 (true = 8x, false = 16x) */
    bool valid;             /* Ознака коректності розрахунку */
} stm32_brr_t;

/* Результати розрахунку конфігурації для NXP LPC */
typedef struct {
    uint32_t f_pclk;        /* Тактова частота шини периферії PCLK (Гц) */
    uint32_t target_baud;   /* Цільова швидкість передачі (бод) */
    uint32_t real_baud;     /* Фактично отримана швидкість (бод) */
    double error_percent;   /* Відносна похибка швидкості (%) */
    uint16_t dll_dlm;       /* 16-бітний базовий дільник (U0DLM:U0DLL) */
    uint8_t divaddval;      /* Чисельник дробової добавки FDR [0..14] */
    uint8_t mulval;         /* Знаменник дробового множника FDR [1..15] */
    bool valid;             /* Ознака коректності розрахунку */
} nxp_lpc_brr_t;

/* Розрахунок значення регістра USART_BRR для мікроконтролерів STM32 */
stm32_brr_t stm32_calc_brr(uint32_t f_ck, uint32_t target_baud, bool over8) {
    stm32_brr_t res = {0};
    res.f_ck = f_ck;
    res.target_baud = target_baud;
    res.over8 = over8;

    if (f_ck == 0 || target_baud == 0) return res;

    uint32_t oversampling = over8 ? 8 : 16;
    double usartdiv = (double)f_ck / (double)(oversampling * target_baud);

    /* Апаратні обмеження дільника STM32: від 1.0 до 4095.9375 */
    if (usartdiv < 1.0 || usartdiv >= 4096.0) {
        return res;
    }

    if (!over8) {
        /* Режим 16x передискретизації: формат 12.4 з фіксованою комою */
        uint32_t mantissa = (uint32_t)usartdiv;
        double frac_part = usartdiv - (double)mantissa;
        uint32_t fraction = (uint32_t)round(frac_part * 16.0);

        /* Захист від переповнення дробової частини при округленні */
        if (fraction >= 16) {
            mantissa += 1;
            fraction = 0;
        }

        res.mantissa = (uint16_t)mantissa;
        res.fraction = (uint8_t)fraction;
        res.brr_value = (uint16_t)((mantissa << 4) | (fraction & 0x0F));
        
        double real_div = (double)mantissa + ((double)fraction / 16.0);
        res.real_baud = (uint32_t)round((double)f_ck / (16.0 * real_div));
    } else {
        /* Режим 8x передискретизації: мантиса в [15:4], дріб у [2:0], біт [3] = 0 */
        uint32_t mantissa = (uint32_t)usartdiv;
        double frac_part = usartdiv - (double)mantissa;
        uint32_t fraction = (uint32_t)round(frac_part * 8.0);

        if (fraction >= 8) {
            mantissa += 1;
            fraction = 0;
        }

        res.mantissa = (uint16_t)mantissa;
        res.fraction = (uint8_t)fraction;
        res.brr_value = (uint16_t)((mantissa << 4) | (fraction & 0x07));
        
        double real_div = (double)mantissa + ((double)fraction / 8.0);
        res.real_baud = (uint32_t)round((double)f_ck / (8.0 * real_div));
    }

    res.error_percent = ((double)res.real_baud - (double)target_baud) / (double)target_baud * 100.0;
    res.valid = true;
    return res;
}

/* Розрахунок оптимальних регістрів FDR та DLL/DLM для NXP LPC */
nxp_lpc_brr_t nxp_lpc_calc_brr(uint32_t f_pclk, uint32_t target_baud) {
    nxp_lpc_brr_t best = {0};
    best.f_pclk = f_pclk;
    best.target_baud = target_baud;
    double min_error = 1e9;

    /* Двовимірний перебір простору раціональних коефіцієнтів FDR */
    for (uint32_t mul = 1; mul <= 15; mul++) {
        for (uint32_t divadd = 0; divadd < mul; divadd++) {
            double fr_mult = 1.0 + ((double)divadd / (double)mul);
            double ideal_dl = (double)f_pclk / (16.0 * (double)target_baud * fr_mult);
            uint32_t dl = (uint32_t)round(ideal_dl);

            if (dl < 1 || dl > 65535) continue;

            double real_baud = (double)f_pclk / (16.0 * (double)dl * fr_mult);
            double err = fabs((real_baud - (double)target_baud) / (double)target_baud * 100.0);

            if (err < min_error) {
                min_error = err;
                best.dll_dlm = (uint16_t)dl;
                best.divaddval = (uint8_t)divadd;
                best.mulval = (uint8_t)mul;
                best.real_baud = (uint32_t)round(real_baud);
                best.error_percent = (real_baud - (double)target_baud) / (double)target_baud * 100.0;
                best.valid = true;
            }
        }
    }
    return best;
}

/* Потактова емуляція проходження 10-бітового кадру UART через дробовий дільник */
bool simulate_uart_reception(uint32_t f_ck, uint32_t target_baud, uint16_t mantissa, uint8_t fraction, uint8_t mod) {
    uint32_t acc = 0;
    uint32_t total_ck_ticks = 0;
    double bit_period_ideal_ticks = (double)f_ck / (double)target_baud;

    printf("  [Емуляція кадру 8-N-1 (f_ck=%u Гц, baud=%u, N=%u, F=%u/%u)]\n",
           f_ck, target_baud, mantissa, fraction, mod);

    /* Симуляція 10 бітів: 1 старт-біт, 8 бітів даних, 1 стоп-біт */
    for (uint32_t bit = 0; bit < 10; bit++) {
        double bit_start_ideal = (double)bit * bit_period_ideal_ticks;
        double bit_center_ideal = bit_start_ideal + 0.5 * bit_period_ideal_ticks;
        uint32_t sample_8_tick = 0;

        /* Бітовий інтервал формується 16 вихідними стробами передискретизації */
        for (uint32_t sample = 0; sample < 16; sample++) {
            acc += fraction;
            uint32_t step = mantissa;
            if (acc >= mod) {
                acc -= mod;
                step += 1; /* Переповнення акумулятора: подовжуємо цикл на 1 такт */
            }
            total_ck_ticks += step;
            if (sample == 8) sample_8_tick = total_ck_ticks;
        }

        /* Розрахунок фазового зміщення центрального стробу від ідеалу */
        double phase_error_ticks = (double)sample_8_tick - (bit_start_ideal + 8.5 * (bit_period_ideal_ticks / 16.0));
        double phase_error_fraction = phase_error_ticks / bit_period_ideal_ticks;

        printf("    Біт %2u: ідеал_центр=%8.1f тактів, строб8=%8u тактів, зсув=%+6.3f біта\n",
               bit, bit_center_ideal, sample_8_tick, phase_error_fraction);

        /* Якщо фазовий зсув перевищує 40% від інтервалу біта — строб виходить за захисне вікно */
        if (fabs(phase_error_fraction) > 0.40) {
            printf("    [!] ПОМИЛКА КАДРУ: строб випав за межі допустимого вікна на біті %u!\n", bit);
            return false;
        }
    }
    printf("    [✓] Успішно: усі 10 бітів надійно застробовано в межах захисного вікна.\n");
    return true;
}

int main(void) {
    printf("=== КАЛЬКУЛЯТОР ДРОБОВИХ ДІЛЬНИКІВ BAUD RATE ===\n\n");

    /* Тест 1: Швидкісний UART 921600 бод на шині STM32 APB1 (42 МГц) */
    printf("1. Розрахунок STM32 USART_BRR (f_ck = 42 МГц, ціль = 921600 бод):\n");
    stm32_brr_t s1_16 = stm32_calc_brr(42000000, 921600, false);
    printf("   [OVER8=0, 16x]: BRR=0x%04X (Мантиса=%u, Дріб=%u/16) -> Реал=%u бод, Похибка=%+.2f%%\n",
           s1_16.brr_value, s1_16.mantissa, s1_16.fraction, s1_16.real_baud, s1_16.error_percent);

    stm32_brr_t s1_8 = stm32_calc_brr(42000000, 921600, true);
    printf("   [OVER8=1,  8x]: BRR=0x%04X (Мантиса=%u, Дріб=%u/8)  -> Реал=%u бод, Похибка=%+.2f%%\n",
           s1_8.brr_value, s1_8.mantissa, s1_8.fraction, s1_8.real_baud, s1_8.error_percent);

    /* Тест 2: Спеціальний протокол Futaba S.Bus (100000 бод на шині 84 МГц) */
    printf("\n2. Розрахунок S.Bus 100000 бод (f_ck = 84 МГц):\n");
    stm32_brr_t s2 = stm32_calc_brr(84000000, 100000, false);
    printf("   [OVER8=0, 16x]: BRR=0x%04X (Мантиса=%u, Дріб=%u/16) -> Реал=%u бод, Похибка=%+.2f%%\n",
           s2.brr_value, s2.mantissa, s2.fraction, s2.real_baud, s2.error_percent);

    /* Тест 3: NXP LPC Fractional Baud Generator (115200 бод при тактовій 12 МГц) */
    printf("\n3. Розрахунок NXP LPC FDR (f_pclk = 12 МГц, ціль = 115200 бод):\n");
    nxp_lpc_brr_t lpc = nxp_lpc_calc_brr(12000000, 115200);
    printf("   DLL/DLM=%u, DIVADDVAL=%u, MULVAL=%u -> Реал=%u бод, Похибка=%+.2f%%\n\n",
           lpc.dll_dlm, lpc.divaddval, lpc.mulval, lpc.real_baud, lpc.error_percent);

    /* Запуск потактової симуляції */
    simulate_uart_reception(42000000, 921600, s1_16.mantissa, s1_16.fraction, 16);

    return 0;
}
