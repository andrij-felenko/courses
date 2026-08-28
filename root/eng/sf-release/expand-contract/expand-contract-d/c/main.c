/* Фаза розширення (Expand): додано нову структуру і нову функцію */
typedef struct {
    const char* filepath;
    int timeout_ms;
    int compression_level; /* Нове поле */
    bool sync_to_disk;     /* Нове поле */
} config_options_t;

/* Новий цільовий метод */
int config_save_ex(const config_options_t* opts);

/* Старий метод перетворюється на адаптер (Shim), що викликає новий */
int config_save(const char* filepath, int timeout_ms) {
    config_options_t opts;
    opts.filepath = filepath;
    opts.timeout_ms = timeout_ms;
    opts.compression_level = 0; // Безпечне значення за замовчуванням
    opts.sync_to_disk = true;
    return config_save_ex(&opts);
}
