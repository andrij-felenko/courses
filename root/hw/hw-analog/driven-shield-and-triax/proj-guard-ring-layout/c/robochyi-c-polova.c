// Польова self-test перевірка охоронного кільця.
// MCU заряджає високоомний вузол, відмикає приведення, вмикає агресор +5 В
// і за відомий час міряє дрейф напруги вузла через ADC.
// Витік I = C * dU/dt; великий витік => кільце має обхід (щілина / флюс / маска).
#include <stdint.h>
#include <stdbool.h>

// --- Платозалежні примітиви (заглушки під конкретний HAL) ----------------
extern void     node_drive_to(float volts);   // буфер жене вузол на volts
extern void     node_release(void);           // вузол лишається на власному R (буфер у Hi-Z)
extern void     aggressor_set(bool on);        // подати/зняти +5 В на сусідній «брудний» вузол
extern float    adc_read_node_volts(void);     // прочитати напругу вузла через ADC
extern void     delay_ms(uint32_t ms);
extern void     log_line(const char *s);

// --- Параметри вузла й тесту (з даташита й розрахунку) --------------------
#define NODE_CAP_F        22.0e-12f   // сумарна ємність вузла (вхід ОП + монтаж), Ф
#define SETTLE_DROP_V     2.5f        // заряджаємо вузол до середини шкали
#define DRIFT_WINDOW_MS   200u        // вікно вимірювання дрейфу
#define LEAK_LIMIT_A      5.0e-12f    // поріг придатності: 5 пА (з запасом над ціллю)

// Один прохід: повертає виміряний витік у вузол, А.
static float measure_node_leakage(void) {
    node_drive_to(SETTLE_DROP_V);   // підтягнули вузол на 2.5 В
    delay_ms(20);                   // дали встановитися
    float u0 = adc_read_node_volts();

    aggressor_set(true);            // увімкнули поряд +5 В — максимально провокуємо витік
    node_release();                 // ВІДМИКАЄМО приведення: тепер вузол тримає лише власний R
    delay_ms(DRIFT_WINDOW_MS);      // даємо витоку попрацювати фіксований час
    float u1 = adc_read_node_volts();

    aggressor_set(false);
    node_drive_to(SETTLE_DROP_V);   // повернули вузол у робочу точку

    // dU/dt за вікно; I = C * dU/dt. Беремо модуль: напрям залежить від того,
    // куди тягне переважний витік (до +5 В вузол повзе вгору).
    float du = u1 - u0;
    if (du < 0.0f) du = -du;
    float dt = (float)DRIFT_WINDOW_MS * 1.0e-3f;     // мс -> с
    return NODE_CAP_F * (du / dt);                    // А
}

// Вирок про кільце: усереднюємо кілька проходів проти шуму ADC.
bool guard_ring_self_test(void) {
    const int N = 8;
    float acc = 0.0f;
    for (int i = 0; i < N; ++i)
        acc += measure_node_leakage();
    float i_leak = acc / (float)N;

    // i_leak = C * dU/dt
    //   справне кільце:  dU за 200 мс мізерний  => одиниці фемто-пікоампер
    //   обхід у кільці:  вузол помітно повзе    => десятки пА і вище
    if (i_leak > LEAK_LIMIT_A) {
        log_line("GUARD: FAIL — вузол пливе, кільце має обхід (щілина/флюс/маска)");
        return false;
    }
    log_line("GUARD: OK — вузол тримається, кільце перехоплює витік");
    return true;
}
