/* main.c — зчитування диференційного каналу з фільтрацією.
 *
 * Прошивка робить дві речі. Перша — тягне з ADS1220 сирі коди й проганяє
 * їх крізь ковзне усереднення з відкиданням викидів. Друга, і для цієї
 * теми головніша, — щохвилини друкує в термінал розмах вікна в LSB та
 * оцінку кількості чесних розрядів. Саме ці два числа кажуть, чи вдалося
 * розведення: на правильно зонованій платі з суцільним полігоном розмах
 * лишається в одиницях LSB, на розрізаній землі росте до сотень.
 */
#include <stdio.h>

#include "ads1220.h"
#include "filter.h"
#include "platform.h"

/* Друкуємо не кожен відлік: при 20 SPS звіт раз на 64 вибірки — це раз
 * на три з гаком секунди, і термінал лишається читабельним. */
#define REPORT_EVERY 64u

/* Скільки збоїв обміну поспіль терпимо, перш ніж піднімати чип наново. */
#define FAULTS_BEFORE_RESET 3u

/* Скидання й запуск чипа. Повертає true, коли АЦП справді налаштований. */
static bool bring_up(void)
{
    ads1220_status_t st = ads1220_init();
    if (st != ADS1220_OK) {
        printf("АЦП не піднявся: %s\r\n", ads1220_strerror(st));
        return false;
    }

    st = ads1220_start();
    if (st != ADS1220_OK) {
        printf("АЦП не почав перетворення: %s\r\n", ads1220_strerror(st));
        return false;
    }

    printf("АЦП готовий: AIN0/AIN1, G = %d, Vref = 3.300 В, 20 SPS\r\n", ADS1220_GAIN);
    return true;
}

static void report(const robust_filter_t *f, int32_t filtered_code)
{
    const int32_t nv = ads1220_code_to_nanovolts(filtered_code);
    const uint32_t total = f->accepted + f->rejected;

    printf("U = %ld нВ | розмах вікна = %ld LSB | ENOB ~ %u біт | викидів %lu з %lu\r\n",
           (long)nv,
           (long)robust_filter_spread(f),
           (unsigned)robust_filter_enob(f),
           (unsigned long)f->rejected,
           (unsigned long)total);
}

int main(void)
{
    board_init();

    robust_filter_t filter;
    robust_filter_init(&filter);

    while (!bring_up()) {
        /* Найчастіша причина — живлення аналогового домену ще не вийшло
         * на режим після ввімкнення: LDO за феритовою бусиною піднімається
         * повільніше за цифрову шину. Чекаємо й пробуємо ще раз. */
        board_delay_ms(200u);
    }

    uint32_t samples = 0u;
    uint32_t faults = 0u;

    for (;;) {
        int32_t code = 0;
        ads1220_status_t st = ads1220_read(&code);

        if (st == ADS1220_ERR_SATURATED) {
            /* Не збій зв'язку, а стан входу: міст розбалансовано або
             * обірвано провід давача. Чип живий, перепідіймати нема чого. */
            printf("Вхід за межами шкали (код %ld) — перевірте баланс мосту\r\n", (long)code);
            faults = 0u;
            continue;
        }

        if (st != ADS1220_OK) {
            faults++;
            printf("Збій %lu: %s\r\n", (unsigned long)faults, ads1220_strerror(st));

            if (faults >= FAULTS_BEFORE_RESET) {
                /* Просідання живлення від кидка струму цифрової частини
                 * здатне скинути чип у стандартну конфігурацію. Мовчки
                 * читати з нього далі — гірше, ніж не читати зовсім. */
                robust_filter_init(&filter);
                faults = 0u;
                while (!bring_up()) {
                    board_delay_ms(200u);
                }
            }
            continue;
        }

        faults = 0u;

        int32_t filtered = 0;
        if (!robust_filter_push(&filter, code, &filtered)) {
            continue; /* вікно ще наповнюється */
        }

        samples++;
        if ((samples % REPORT_EVERY) == 0u) {
            report(&filter, filtered);
        }
    }
}
