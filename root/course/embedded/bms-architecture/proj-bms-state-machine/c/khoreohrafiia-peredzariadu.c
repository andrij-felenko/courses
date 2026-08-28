// Поріг «напруги майже зрівнялися»: частка від напруги пакета.
#define PRECHARGE_DONE_FRAC   0.95f   // 95 % — типова інженерна практика
#define PRECHARGE_TIMEOUT_MS  600u    // не зарядилось за цей час → відмова
#define PRECHARGE_SETTLE_MS   20u     // дати головному реально замкнутись

static void precharge_step(uint32_t t)
{
    float u_pack = read_u_pack();
    float u_load = read_u_load();

    // Запобіжник: ємність не набирає напругу вчасно → коротке/несправність.
    if (t - bms.t_enter > PRECHARGE_TIMEOUT_MS) {
        enter_fault(FAULT_PRECHARGE_TIMEOUT);
        return;
    }

    // Критерій успіху — ВИМІР, а не таймер: навантаження дійшло до ~95 %.
    if (u_load >= PRECHARGE_DONE_FRAC * u_pack) {
        cmd_main(true);                // 4) головний — ПЕРШ, ніж прибрати передзаряд
        bms.t_enter = t;               // переустановили годинник під крок ON
        bms.state   = BMS_ON;          // далі довершить on_step(): зніме передзарядний
    }
    // інакше нічого не робимо — ємність ще заряджається, чекаємо наступного кроку
}
