// Мінімальна таблиця ASCII → usage ID (тільки US-layout, нижній регістр).
// Для верхнього регістру потрібен modifier KEY_LSHIFT; кирилиця — неможлива
// без знання системної розкладки хоста (пастка №2 нижче).
struct { char ascii; uint8_t usage; } ascii_map[] = {
    { 'a', 0x04 }, { 'b', 0x05 }, { 'r', 0x15 },
    // ... повна таблиця 'a'-'z': usage 0x04..0x1D
    { ' ', 0x2C }, { '\n', 0x28 },
};

uint8_t ascii_to_usage(char c) {
    for (auto& e : ascii_map)
        if (e.ascii == c) return e.usage;
    return KEY_NONE;
}

// Надрукувати C-рядок символ за символом (тільки US-layout).
void type_string(const char* s) {
    for (; *s; s++) {
        uint8_t u = ascii_to_usage(*s);
        if (u == KEY_NONE) continue;
        key_send(KEY_NONE, u);
        delay(8);          // дати хосту забрати звіт (залежить від bInterval)
        key_release();
        delay(8);
    }
}

// Антибрязкіт — окрема тема про усунення брязкоту контактів.
bool button_pressed_edge();   // повертає true один раз при фронті

void loop() {
    if (button_pressed_edge()) {
        // Комбінація Win+R → відкрити «Виконати»
        key_send(KEY_LGUI, KEY_R);
        delay(8);
        key_release();
        delay(50);         // пауза перед наступним макро

        // Або надрукувати рядок (тільки US-layout, нижній регістр):
        // type_string("hello");
    }
}
