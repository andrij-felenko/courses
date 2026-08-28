uint8_t level = 128;           // спільний рівень переливу; старт — рівно наполовину
const uint8_t STEP = 3;        // на скільки посуваємо рівень за один такт

// Посунути рівень угору/вниз на STEP, не вилізши за межі 0..255.
void nudge(int8_t dir) {       // dir = +1 (до A), −1 (до B), 0 (стоїмо)
    int next = (int)level + dir * STEP;   // рахуємо в int, щоб зловити вихід за край
    if (next < 0)   next = 0;
    if (next > 255) next = 255;
    level = (uint8_t)next;
}
