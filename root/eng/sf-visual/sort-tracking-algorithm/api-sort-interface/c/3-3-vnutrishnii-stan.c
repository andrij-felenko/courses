typedef struct {
    float state[7];             // [u, v, s, r, u_dot, v_dot, s_dot]
    float covariance[7][7];      // Симетрична додатно визначена матриця P
    int track_id;               // Унікальний номер треку
    int class_id;               // Семантичний клас
    int hits;                   // Загальна кількість успішних асоціацій
    int hit_streak;             // Кількість асоціацій поспіль без пропусків
    int age;                    // Кількість кадрів з моменту ініціалізації
    int time_since_update;      // Кількість кадрів з моменту останньої детекції
    bool is_active;             // Прапорець занятості слота в пулі пам'яті
} sort_internal_track_t;
