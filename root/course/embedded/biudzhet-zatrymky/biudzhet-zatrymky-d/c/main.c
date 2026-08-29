/* main.c — бюджети затримки конкретних комплексів.
 *
 * Тут зібрані п'ять трактів зі статті: два контури керування
 * (Stick-to-Motor) і три відеотракти (Glass-to-Glass). Числа ланок —
 * не константи «зі стелі», а параметри заліза: частота опитування,
 * швидкість шини, частота пакетів, кадрова частота. Змінюєш параметр —
 * бюджет перераховується сам, і саме заради цього тракт описується
 * таблицею ланок, а не однією підсумковою цифрою.
 *
 * Збірка: cc -std=c11 -O2 -Wall -Wextra main.c latency.c report.c -o latency
 */
#include <stdio.h>
#include <stdlib.h>
#include "latency.h"
#include "report.h"

/* Конфігурація тракту — це дані, і помилка в ній програмістська, а не
   робоча: тракт із мовчки пропущеною ланкою брехав би на десятки
   мілісекунд. Тому падаємо голосно й одразу. */
static void must(lat_pipeline *p, lat_stage st)
{
    const lat_status rc = lat_pipeline_add(p, st);
    if (rc != LAT_OK) {
        fprintf(stderr, "тракт «%s», ланка «%s»: %s\n",
                p->title, st.name, lat_strerror(rc));
        exit(EXIT_FAILURE);
    }
}

/* --- Контур керування: сучасний цифровий ---------------------------------
 * ELRS 500 Гц + CRSF на 2 Мбіт/с + польотний контролер на 4 кГц + DShot600.
 * rf_synced вмикає EdgeTX Mixer Sync: мікшер пульта рахує кадр рівно перед
 * тайм-слотом радіомодуля, і чекання слота згортається зі "пів періоду"
 * до сталого зсуву.
 *
 * Фільтрів гіроскопа тут навмисно немає: їхня групова затримка лежить у
 * контурі стабілізації (гіроскоп -> PID), а не на шляху команди зі стика.
 */
static void build_stick_modern(lat_pipeline *p, bool rf_synced)
{
    lat_pipeline_init(p, rf_synced ? "Керування: цифра, фаза зведена"
                                   : "Керування: цифра, фаза не зведена");

    must(p, lat_periodic("АЦП стика, 1 кГц", 1000.0, false, 0.0));
    must(p, lat_band("IIR-фільтр стика", 0.5, 0.5, 1.0));
    must(p, lat_serial("UART CRSF, 2 Мбіт/с", 26u, 2000000.0, 10u));
    must(p, lat_periodic("Тайм-слот ELRS, 500 Гц", 500.0, rf_synced, 0.35));
    must(p, lat_fixed("Пакет у повітрі", 1.1));
    must(p, lat_band("Декодування в приймачі", 0.3, 0.5, 0.8));
    must(p, lat_periodic("Цикл PID, 4 кГц", 4000.0, false, 0.0));
    must(p, lat_fixed("Розрахунок мікшера", 0.04));
    must(p, lat_fixed("Кадр DShot600", 16.0 * 1.67 / 1000.0));
    must(p, lat_fixed("Комутація ключів ESC", 0.03));
    must(p, lat_physical(lat_band("Наростання струму (tau_e)", 0.2, 0.5, 1.5)));
    must(p, lat_physical(lat_band("Розгін гвинта 5\" (tau_m)", 15.0, 20.0, 25.0)));
}

/* --- Контур керування: застарілий аналоговий -----------------------------
 * Опитування стиків на 125 Гц, SBUS, радіолінк 50 Гц, PPM на виході
 * приймача і аналоговий PWM на регуляторах. Механіка та сама — і саме
 * тому різниця в підсумку вся електронна.
 */
static void build_stick_legacy(lat_pipeline *p)
{
    lat_pipeline_init(p, "Керування: аналоговий тракт");

    must(p, lat_periodic("АЦП стика, 125 Гц", 125.0, false, 0.0));
    must(p, lat_serial("Шина SBUS, 100 кбіт/с", 25u, 100000.0, 10u));
    must(p, lat_periodic("Радіокадр, 50 Гц", 50.0, false, 0.0));
    must(p, lat_periodic("Вивід PPM приймача, 50 Гц", 50.0, false, 0.0));
    must(p, lat_periodic("Цикл PID, 1 кГц", 1000.0, false, 0.0));
    must(p, lat_fixed("Розрахунок мікшера", 0.04));
    must(p, lat_periodic("Аналоговий PWM, 50 Гц", 50.0, false, 0.0));
    must(p, lat_physical(lat_band("Наростання струму (tau_e)", 0.2, 0.5, 1.5)));
    must(p, lat_physical(lat_band("Розгін гвинта 5\" (tau_m)", 15.0, 20.0, 25.0)));
}

/* --- Відео: аналоговий тракт ---------------------------------------------
 * Растр окулярів зафазований із синхросигналом камери — приймач не
 * буферизує кадр, він малює рядок у міру надходження. Звідси синхронна
 * ланка дисплея з мізерним люфтом, а не пів періоду очікування.
 */
static void build_video_analog(lat_pipeline *p, double fps)
{
    lat_pipeline_init(p, "Відео: аналог (PAL/NTSC)");

    must(p, lat_physical(lat_band("Експозиція матриці", 1.0, 2.0, 5.0)));
    must(p, lat_physical(lat_periodic("Построкове зчитування", fps, false, 0.0)));
    must(p, lat_band("DSP камери", 1.5, 3.5, 6.0));
    must(p, lat_fixed("FM-модулятор", 0.02));
    must(p, lat_band("Демодулятор приймача", 0.05, 0.1, 0.2));
    must(p, lat_periodic("Растр окулярів", fps, true, 0.2));
    must(p, lat_physical(lat_fixed("Відгук пікселя OLED", 0.1)));
}

/* --- Відео: цифрове HD зі зрізовим кодуванням ----------------------------
 * Кодер не чекає кадру: зріз із 16–32 рядків іде в ефір, поки матриця ще
 * експонує низ картинки. Тому окремої ланки «кадровий буфер кодера» тут
 * немає — і саме її відсутність відрізняє FPV-систему від IP-камери.
 */
static void build_video_digital(lat_pipeline *p, double fps, double display_hz)
{
    lat_pipeline_init(p, "Відео: цифрове HD (зрізи)");

    must(p, lat_physical(lat_band("Експозиція матриці", 1.0, 2.0, 8.3)));
    must(p, lat_physical(lat_periodic("Построкове зчитування", fps, false, 0.0)));
    must(p, lat_band("ISP на льоту", 0.5, 1.0, 2.0));
    must(p, lat_band("Зрізове кодування", 1.5, 2.5, 3.5));
    must(p, lat_band("OFDM та інтерлівінг", 1.0, 2.0, 3.0));
    must(p, lat_band("Пакет у повітрі", 1.0, 2.0, 4.0));
    must(p, lat_band("Апаратний декодер VPU", 2.0, 3.0, 5.0));
    must(p, lat_band("Адаптивний буфер джитера", 2.0, 4.0, 6.0));
    must(p, lat_periodic("Прямий вивід на дисплей", display_hz, false, 0.0));
    must(p, lat_physical(lat_fixed("Відгук пікселя OLED", 0.1)));
}

/* --- Відео: IP-стрім через LTE -------------------------------------------
 * Кадровий кодер — жорстка підлога в один повний період кадру: DCT не
 * починається, поки кадр не ліг у буфер цілком. Далі до нього додаються
 * черги ядра, буфер джитера мережі й композитор віконної системи.
 */
static void build_video_ip(lat_pipeline *p, double fps, double jitter_buffer_ms)
{
    lat_pipeline_init(p, "Відео: LTE / IP-стрім");

    must(p, lat_physical(lat_band("Експозиція матриці", 1.0, 2.0, 8.3)));
    must(p, lat_physical(lat_periodic("Построкове зчитування", fps, false, 0.0)));
    must(p, lat_band("ISP камери", 0.5, 1.0, 2.0));
    must(p, lat_fixed("Кадровий буфер кодера", 1000.0 / fps));
    must(p, lat_band("Обчислення H.264", 5.0, 10.0, 20.0));
    must(p, lat_band("Стек сокетів і qdisc", 15.0, 25.0, 40.0));
    must(p, lat_band("Радіотракт LTE", 20.0, 40.0, 80.0));
    must(p, lat_fixed("Буфер джитера мережі", jitter_buffer_ms));
    must(p, lat_band("Декодер приймача", 5.0, 10.0, 20.0));
    must(p, lat_band("Композитор ОС", 16.7, 25.0, 33.3));
    must(p, lat_physical(lat_band("Відгук пікселя LCD", 5.0, 8.0, 15.0)));
}

/* Контур оператора замикається двічі: команда летить туди, картинка
   повертається назад. Фазу накопичує сума обох трактів, і саме її
   порівнюють зі 100–150 мс, а не окремий Stick-to-Motor. */
static void closed_loop(const char *label, const lat_pipeline *cmd,
                        const lat_pipeline *video, double control_hz, double speed_mps)
{
    const lat_budget total = lat_budget_sum(lat_budget_of(cmd), lat_budget_of(video));
    rep_dynamics(label, total, control_hz, speed_mps);
}

int main(void)
{
    lat_pipeline stick_modern, stick_unsynced, stick_legacy;
    lat_pipeline video_analog, video_digital, video_ip;
    const lat_pipeline *sticks[3];
    const lat_pipeline *videos[3];

    const double control_hz = 2.5;  /* смуга ручного маневрування оператора */
    const double speed_mps  = 25.0; /* 90 км/год */

    build_stick_modern(&stick_modern, true);
    build_stick_modern(&stick_unsynced, false);
    build_stick_legacy(&stick_legacy);

    build_video_analog(&video_analog, 60.0);
    build_video_digital(&video_digital, 60.0, 120.0);
    build_video_ip(&video_ip, 30.0, 60.0);

    /* 1. Два контури керування в подробицях. */
    rep_pipeline(&stick_modern);
    rep_dynamics(stick_modern.title, lat_budget_of(&stick_modern), control_hz, speed_mps);

    rep_pipeline(&stick_legacy);
    rep_dynamics(stick_legacy.title, lat_budget_of(&stick_legacy), control_hz, speed_mps);

    /* 2. Ціна фазування: та сама залізяка, зведена й не зведена за фазою.
          Різниця лише в одній ланці — і вона вилазить у джитер. */
    sticks[0] = &stick_modern;
    sticks[1] = &stick_unsynced;
    sticks[2] = &stick_legacy;
    rep_compare("КОНТУР КЕРУВАННЯ: Stick-to-Motor", sticks, 3u);

    /* 3. Три відеотракти. Аналог виграє не роздільною здатністю, а
          відсутністю буферів; IP програє не радіо, а чергами ОС. */
    rep_pipeline(&video_digital);
    videos[0] = &video_analog;
    videos[1] = &video_digital;
    videos[2] = &video_ip;
    rep_compare("ВІДЕОТРАКТ: Glass-to-Glass", videos, 3u);

    /* 4. Замкнений контур оператора: команда плюс картинка. */
    closed_loop("Цифра + аналогове відео", &stick_modern, &video_analog,
                control_hz, speed_mps);
    closed_loop("Цифра + цифрове HD", &stick_modern, &video_digital,
                control_hz, speed_mps);
    closed_loop("Аналог + LTE-стрім", &stick_legacy, &video_ip,
                control_hz, speed_mps);

    return EXIT_SUCCESS;
}
