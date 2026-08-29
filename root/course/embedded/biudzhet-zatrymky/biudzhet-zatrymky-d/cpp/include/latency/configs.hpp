// configs.hpp — бюджети конкретних комплексів як константи компіляції.
//
// Числа ланок — не константи «зі стелі», а параметри заліза: частота
// опитування, швидкість шини, частота пакетів, кадрова частота. Оскільки
// всі конструктори constexpr, зібраний бюджет доступний ще до запуску, і
// проєктні межі перевіряються static_assert'ами внизу файлу: конфігурація,
// що вилізла за бюджет, просто не збереться.
#pragma once

#include "latency/pipeline.hpp"

namespace latency::configs {

using namespace std::chrono_literals;

// --- Контур керування: сучасний цифровий -----------------------------------
// ELRS 500 Гц + CRSF на 2 Мбіт/с + польотний контролер на 4 кГц + DShot600.
// phase_locked вмикає EdgeTX Mixer Sync: мікшер пульта рахує кадр рівно перед
// тайм-слотом радіомодуля, і чекання слота згортається зі «пів періоду» до
// сталого зсуву.
//
// Фільтрів гіроскопа тут навмисно немає: їхня групова затримка лежить у
// контурі стабілізації (гіроскоп -> PID), а не на шляху команди зі стика.
constexpr Pipeline<12> stick_digital(bool phase_locked) {
    Pipeline<12> p{phase_locked ? "Керування: цифра, фаза зведена"
                                : "Керування: цифра, фаза не зведена"};
    p.add(periodic("АЦП стика, 1 кГц", 1000.0))
     .add(band("IIR-фільтр стика", 0.5ms, 0.5ms, 1.0ms))
     .add(serial("UART CRSF, 2 Мбіт/с", 26, 2'000'000.0))
     .add(phase_locked ? periodic_locked("Тайм-слот ELRS, 500 Гц", 500.0, 0.35ms)
                       : periodic("Тайм-слот ELRS, 500 Гц", 500.0))
     .add(fixed("Пакет у повітрі", 1.1ms))
     .add(band("Декодування в приймачі", 0.3ms, 0.5ms, 0.8ms))
     .add(periodic("Цикл PID, 4 кГц", 4000.0))
     .add(fixed("Розрахунок мікшера", 0.04ms))
     .add(fixed("Кадр DShot600", Ms{16 * 1.67 / 1000.0}))
     .add(fixed("Комутація ключів ESC", 0.03ms))
     .add(physical(band("Наростання струму (tau_e)", 0.2ms, 0.5ms, 1.5ms)))
     .add(physical(band("Розгін гвинта 5\" (tau_m)", 15.0ms, 20.0ms, 25.0ms)));
    return p;
}

// --- Контур керування: застарілий аналоговий -------------------------------
// Опитування стиків на 125 Гц, SBUS, радіолінк 50 Гц, PPM на виході приймача
// й аналоговий PWM на регуляторах. Механіка та сама — і саме тому вся
// різниця в підсумку електронна.
constexpr Pipeline<9> stick_analog() {
    Pipeline<9> p{"Керування: аналоговий тракт"};
    p.add(periodic("АЦП стика, 125 Гц", 125.0))
     .add(serial("Шина SBUS, 100 кбіт/с", 25, 100'000.0))
     .add(periodic("Радіокадр, 50 Гц", 50.0))
     .add(periodic("Вивід PPM приймача, 50 Гц", 50.0))
     .add(periodic("Цикл PID, 1 кГц", 1000.0))
     .add(fixed("Розрахунок мікшера", 0.04ms))
     .add(periodic("Аналоговий PWM, 50 Гц", 50.0))
     .add(physical(band("Наростання струму (tau_e)", 0.2ms, 0.5ms, 1.5ms)))
     .add(physical(band("Розгін гвинта 5\" (tau_m)", 15.0ms, 20.0ms, 25.0ms)));
    return p;
}

// --- Відео: аналоговий тракт ------------------------------------------------
// Растр окулярів зведено з синхросигналом камери — приймач не буферизує кадр,
// він малює рядок у міру надходження. Звідси синхронна ланка дисплея з
// мізерним люфтом, а не пів періоду очікування.
constexpr Pipeline<8> video_analog(double fps) {
    Pipeline<8> p{"Відео: аналог (PAL/NTSC)"};
    p.add(physical(band("Експозиція матриці", 1.0ms, 2.0ms, 5.0ms)))
     .add(physical(periodic("Построкове зчитування", fps)))
     .add(band("DSP камери", 1.5ms, 3.5ms, 6.0ms))
     .add(fixed("FM-модулятор", 0.02ms))
     .add(band("Демодулятор приймача", 0.05ms, 0.1ms, 0.2ms))
     .add(periodic_locked("Растр окулярів", fps, 0.2ms))
     .add(physical(fixed("Відгук пікселя OLED", 0.1ms)));
    return p;
}

// --- Відео: цифрове HD зі зрізовим кодуванням -------------------------------
// Кодер не чекає кадру: зріз із 16–32 рядків іде в ефір, поки матриця ще
// експонує низ картинки. Тому окремої ланки «кадровий буфер кодера» тут
// немає — і саме її відсутність відрізняє FPV-систему від IP-камери.
constexpr Pipeline<12> video_digital(double fps, double display_hz) {
    Pipeline<12> p{"Відео: цифрове HD (зрізи)"};
    p.add(physical(band("Експозиція матриці", 1.0ms, 2.0ms, 8.3ms)))
     .add(physical(periodic("Построкове зчитування", fps)))
     .add(band("ISP на льоту", 0.5ms, 1.0ms, 2.0ms))
     .add(band("Зрізове кодування", 1.5ms, 2.5ms, 3.5ms))
     .add(band("OFDM та інтерлівінг", 1.0ms, 2.0ms, 3.0ms))
     .add(band("Пакет у повітрі", 1.0ms, 2.0ms, 4.0ms))
     .add(band("Апаратний декодер VPU", 2.0ms, 3.0ms, 5.0ms))
     .add(band("Адаптивний буфер джитера", 2.0ms, 4.0ms, 6.0ms))
     .add(periodic("Прямий вивід на дисплей", display_hz))
     .add(physical(fixed("Відгук пікселя OLED", 0.1ms)));
    return p;
}

// --- Відео: IP-стрім через LTE ----------------------------------------------
// Кадровий кодер — жорстка підлога в один повний період кадру: DCT не
// починається, поки кадр не ліг у буфер цілком. Далі додаються черги ядра,
// буфер джитера мережі й композитор віконної системи.
constexpr Pipeline<12> video_ip(double fps, Ms jitter_buffer) {
    Pipeline<12> p{"Відео: LTE / IP-стрім"};
    p.add(physical(band("Експозиція матриці", 1.0ms, 2.0ms, 8.3ms)))
     .add(physical(periodic("Построкове зчитування", fps)))
     .add(band("ISP камери", 0.5ms, 1.0ms, 2.0ms))
     .add(fixed("Кадровий буфер кодера", Ms{1000.0 / fps}))
     .add(band("Обчислення H.264", 5.0ms, 10.0ms, 20.0ms))
     .add(band("Стек сокетів і qdisc", 15.0ms, 25.0ms, 40.0ms))
     .add(band("Радіотракт LTE", 20.0ms, 40.0ms, 80.0ms))
     .add(fixed("Буфер джитера мережі", jitter_buffer))
     .add(band("Декодер приймача", 5.0ms, 10.0ms, 20.0ms))
     .add(band("Композитор ОС", 16.7ms, 25.0ms, 33.3ms))
     .add(physical(band("Відгук пікселя LCD", 5.0ms, 8.0ms, 15.0ms)));
    return p;
}

// --- Готові конфігурації ----------------------------------------------------
// Об'єкти зі статичним часом життя: жодного підрахунку в рантаймі,
// звітам лишається тільки надрукувати готові числа.
inline constexpr auto kStickLocked   = stick_digital(true);
inline constexpr auto kStickFree     = stick_digital(false);
inline constexpr auto kStickAnalog   = stick_analog();
inline constexpr auto kVideoAnalog   = video_analog(60.0);
inline constexpr auto kVideoDigital  = video_digital(60.0, 120.0);
inline constexpr auto kVideoIp       = video_ip(30.0, 60.0ms);

// --- Проєктні межі, перевірені компілятором ---------------------------------
// Електронна частина сучасного тракту керування мусить лишатися одиницями
// мілісекунд: усе решта в ньому — фізика мотора, і торгуватися можна лише
// за неї (легший гвинт, інший KV).
static_assert(summarize(kStickLocked.track().stages).electronic < Ms{6.0},
              "електроніка цифрового тракту вилізла за 6 мс — шукай зайвий буфер");

// Зведення фаз чіпає рівно одну ланку, але саме вона визначає джитер тракту.
static_assert(summarize(kStickLocked.track().stages).jitter <
              summarize(kStickFree.track().stages).jitter,
              "фазування мусить зменшувати джитер, інакше воно ні до чого");

// Аналоговий тракт керування програє не механікою, а електронікою.
static_assert(summarize(kStickAnalog.track().stages).electronic > Ms{30.0});

// Зрізове кодування має тримати відео втричі швидшим за IP-стрім.
static_assert(summarize(kVideoDigital.track().stages).typ * 3.0 <
              summarize(kVideoIp.track().stages).typ,
              "цифрове HD втратило перевагу над IP — перевір буфери");

// Найтовща ланка сучасного тракту керування — механіка, а не електроніка.
static_assert(bottleneck(kStickLocked.track().stages)->domain == Domain::Physical);

}  // namespace latency::configs
