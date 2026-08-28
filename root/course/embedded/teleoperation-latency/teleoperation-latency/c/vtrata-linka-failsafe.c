// Пороги тиші в мілісекундах — під конкретну платформу
#define T_HOLD_MS   300u    // коротша тиша: тримати курс
#define T_STOP_MS  1000u    // довша: плавний стоп + маяк
#define T_RTB_MS   5000u    // зовсім довга: політика місії

typedef enum { LINK_NORMAL, LINK_HOLD, LINK_STOP, LINK_RTB } link_state_t;

// silent_ms — скільки триває тиша; оновлює watchdog за heartbeat.
// Повертає, ЩО робити приводу цього такту.
link_state_t link_failsafe(uint32_t silent_ms) {
    if (silent_ms < T_HOLD_MS)  return LINK_NORMAL;  // ефір живий: слухай оператора
    if (silent_ms < T_STOP_MS)  return LINK_HOLD;    // тримай останній курс, не смикай
    if (silent_ms < T_RTB_MS)   return LINK_STOP;    // плавно спинись, увімкни маяк
    return LINK_RTB;                                 // за політикою: чекай або вертайся
}

// Застосування в головному циклі приводу:
void drive_tick(uint32_t now_ms, uint32_t last_hb_ms) {
    uint32_t silent = now_ms - last_hb_ms;           // тиша від останнього серцебиття
    switch (link_failsafe(silent)) {
        case LINK_NORMAL: apply_operator_cmd();      break;  // звичайне телекерування
        case LINK_HOLD:   hold_last_cmd();           break;  // не чіпати кермо
        case LINK_STOP:   ramp_to_stop(); beacon_on(); break; // плавно в нуль + маяк
        case LINK_RTB:    ramp_to_stop(); mission_rtb(); break;
    }
}
