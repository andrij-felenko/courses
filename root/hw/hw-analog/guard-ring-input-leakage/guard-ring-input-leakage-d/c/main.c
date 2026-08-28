// Оцінка струму витоку до і після guard. Якщо корисний струм давача
// співмірний з I_no_guard — guard обовʼязковий; з I_guard — можна жити без нього.
float leak_no_guard(float v_dirty, float v_node, float r_leak) {
    return (v_dirty - v_node) / r_leak;          // повна різниця на опорі
}
float leak_with_guard(float v_offset, float r_leak) {
    return v_offset / r_leak;                     // лишається тільки зсув ОП
}

// приклад: брудний вузол 5 В, вхід 0.1 В, R витоку 1 ГОм, зсув 2 мВ
float Ing = leak_no_guard(5.0f, 0.1f, 1.0e9f);   // 4.9e-9  А  = 4.9 нА
float Ig  = leak_with_guard(0.002f, 1.0e9f);     // 2.0e-12 А  = 2 пА
float gain = Ing / Ig;                            // ≈ 2450
