// Гілки: кожен код — окрема розв'язка, на гарячому шляху низка порівнянь
uint8_t level_branch(uint8_t code) {
    if (code == 0) return 0;
    else if (code == 1) return 10;
    else if (code == 2) return 25;
    else if (code == 3) return 50;
    else return 100;
}

// Таблиця: жодної гілки на гарячому шляху — одне читання за індексом
static const uint8_t LEVEL[5] = { 0, 10, 25, 50, 100 };
uint8_t level_table(uint8_t code) {
    return (code < 5) ? LEVEL[code] : 100;   // одна перевірка меж — і читання
}
