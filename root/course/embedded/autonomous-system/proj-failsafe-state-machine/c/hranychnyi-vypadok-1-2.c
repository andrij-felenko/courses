// повертає «стабільно істинний»: true лише коли ok тримається >= hold секунд
static bool debounce_generic(bool ok, float dt, float hold, float *acc) {
    if (ok) { *acc = 0.0f; return true; }        // здорове — миттєво довіряємо
    *acc += dt;                                    // хворе — накопичуємо час
    return (*acc < hold);                          // ще true, поки не витримали hold
}

static bool debounce_imu(bool ok, float dt) {
    static float acc = 0.0f;
    return debounce_generic(ok, dt, 0.10f, &acc);  // ~100 мс: короткий збій шини — не аварія
}
static bool debounce_link(bool ok, float dt) {
    static float acc = 0.0f;
    return debounce_generic(ok, dt, 3.0f, &acc);   // 3 с тиші — тоді вважаємо зв'язок утраченим
}
