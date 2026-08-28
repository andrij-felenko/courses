#define N_CELLS        4
#define BAL_START_MV   30      // вмикати баланс від цього розкиду
#define BAL_STOP_MV    10      // вимикати, коли зійшлись тісніше (гістерезис)

// Знайти найповнішу й найбіднішу комірку та розкид між ними.
typedef struct { int hi, lo; uint16_t spread_mv; } imbalance_t;

static imbalance_t find_imbalance(const uint16_t mv[N_CELLS])
{
    int hi = 0, lo = 0;
    for (int i = 1; i < N_CELLS; i++) {
        if (mv[i] > mv[hi]) hi = i;   // найповніша — найвища напруга
        if (mv[i] < mv[lo]) lo = i;   // найбідніша — найнижча
    }
    imbalance_t r = { hi, lo, (uint16_t)(mv[hi] - mv[lo]) };
    return r;
}

// Один такт керування балансиром. balancing — стан між викликами (гістерезис).
void balance_step(const uint16_t mv[N_CELLS], bool *balancing)
{
    imbalance_t im = find_imbalance(mv);

    if (!*balancing && im.spread_mv >= BAL_START_MV)
        *balancing = true;                 // розкид виріс — вмикаємось
    else if (*balancing && im.spread_mv <= BAL_STOP_MV)
        *balancing = false;                // зійшлись — спиняємось

    if (!*balancing) { balancer_off(); return; }

    // Пасивний вузол: розряджаємо найповнішу крізь її резистор.
    // Активний вузол: переносимо заряд із найповнішої в найбіднішу.
    transfer_charge(im.hi, im.lo);         // для пасиву lo ігнорується
}
