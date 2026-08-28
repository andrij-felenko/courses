// Статична перевірка під'єднання кільця за нетлистом (фрагмент DRC).
// Перевіряємо ДВА правила, що видно з нетлиста:
//   1) кільце ведене на ПРАВИЛЬНИЙ вузол для даної топології;
//   2) виводи, сусідні з високоомним, лишені порожніми або на кільці.
#include <string.h>
#include <stdbool.h>

typedef enum { CFG_FOLLOWER, CFG_NONINV, CFG_INVERTING } amp_cfg_t;

// Який вузол МУСИТЬ нести кільце для даної топології (канон ADI/Microchip).
static const char *expected_guard_net(amp_cfg_t cfg) {
    switch (cfg) {
        case CFG_FOLLOWER:  return "OUT";    // −IN з'єднано з виходом
        case CFG_NONINV:    return "INV_IN"; // −IN, вузол подільника ЗЗ
        case CFG_INVERTING: return "GND";    // входи на віртуальній землі
    }
    return "?";
}

// guard_net — до якої цепі реально під'єднане кільце в нетлисті.
bool check_guard_net(amp_cfg_t cfg, const char *guard_net) {
    const char *want = expected_guard_net(cfg);
    if (strcmp(guard_net, want) != 0) {
        // Найтиповіша пастка: кільце на GND там, де вузол гуляє з сигналом.
        return false;  // DRC error: кільце на хибному вузлі
    }
    return true;
}

// Сусідні виводи мають бути або не під'єднані (NC), або на тій самій цепі кільця.
bool check_adjacent_pins(const char *pin_net[], int n_adj, const char *guard_net) {
    for (int i = 0; i < n_adj; ++i) {
        bool nc       = (pin_net[i] == 0) || (pin_net[i][0] == '\0');
        bool on_guard = pin_net[i] && (strcmp(pin_net[i], guard_net) == 0);
        if (!nc && !on_guard)
            return false;  // DRC warn: біля вузла «брудний» вивід — подовж шлях витоку
    }
    return true;
}
