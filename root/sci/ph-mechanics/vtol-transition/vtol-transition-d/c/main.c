// стан переходу: викликається щотакту керування (напр. 400 Гц)
// airspeed_mps — повітряна швидкість із давача (не land speed!)
#define V_TRANS   15.0f    // поріг, за яким крило надійно несе, м/с
#define SPINDOWN_MS  5000  // за скільки прибрати газ висіння

void transition_fwd_update(float airspeed_mps, uint32_t now_ms) {
    fwd_throttle = 1.0f;                 // тягнучий гвинт — на розгін

    if (airspeed_mps < V_TRANS) {
        // ще в «дірі»: крило не несе всю вагу — тримаємо висіння повністю,
        // висотний контур сам додає газу вгору, скільки треба
        hover_throttle = hover_alt_hold(); // повне утримання висоти
        t_reached = 0;                     // таймер спуску ще не пущено
    } else {
        // швидкість надійно понад звалювання — крило перебрало вагу.
        // прибираємо газ висіння ПЛАВНО, не ривком, за SPINDOWN_MS
        if (t_reached == 0) t_reached = now_ms;
        float k = (now_ms - t_reached) / (float)SPINDOWN_MS; // 0 → 1
        if (k > 1.0f) k = 1.0f;
        hover_throttle = hover_alt_hold() * (1.0f - k);       // згасання
        if (k >= 1.0f) mode = MODE_FIXED_WING;                // перехід завершено
    }
}
