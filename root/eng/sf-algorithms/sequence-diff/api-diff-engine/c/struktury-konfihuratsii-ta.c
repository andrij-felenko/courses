/* Налаштування процесу порівняння */
typedef struct {
    diff_algo_t algorithm;      /* Обраний алгоритм порівняння */
    size_t context_lines;       /* Кількість рядків контексту довкола змін (типово 3) */
    bool ignore_whitespace_eol; /* Ігнорувати пробільні символи в кінці рядка */
    bool ignore_all_whitespace; /* Ігнорувати всі пробільні символи */
    size_t max_edit_distance;   /* Граничне значення D (0 — без обмежень) */
} diff_config_t;

/* Окремий рядок у структурованому фрагменті diff */
typedef struct {
    diff_op_t op;
    size_t old_line_num; /* 1-індексований номер рядка у файлі A (0 для вставки) */
    size_t new_line_num; /* 1-індексований номер рядка у файлі B (0 для видалення) */
    const char* text;    /* Вказівник на початок тексту рядка */
    size_t length;       /* Довжина рядка в байтах */
} diff_line_entry_t;

/* Структурований фрагмент різниць (Hunk) */
typedef struct {
    size_t old_start;           /* Початковий рядок у файлі A */
    size_t old_count;           /* Кількість рядків з файлу A у фрагменті */
    size_t new_start;           /* Початковий рядок у файлі B */
    size_t new_count;           /* Кількість рядків з файлу B у фрагменті */
    diff_line_entry_t* entries; /* Масив рядків фрагмента */
    size_t entry_count;         /* Кількість елементів у масиві entries */
} diff_hunk_t;

/* Повний результат порівняння */
typedef struct {
    diff_hunk_t* hunks;         /* Масив фрагментів */
    size_t hunk_count;          /* Кількість фрагментів */
    size_t total_deletions;     /* Загальна кількість видалених рядків */
    size_t total_insertions;    /* Загальна кількість доданих рядків */
    size_t edit_distance;       /* Обчислена редакторська відстань D */
} diff_result_t;
