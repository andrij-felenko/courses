// ── ОДИН РАЗ при старті ──────────────────────────────────────────────
bool vision_setup(void) {
    // Бюджет кадру з вимог контуру керування (НЕ вгаданий — заданий задачею).
    const uint32_t budget_us = 60000;       // 60 мс/кадр → ~16 кадрів/с стелею

    // Скільки реально вільно під модель ПІСЛЯ коду, стека, купи, буферів.
    uint32_t free_flash = mcu_free_flash();
    uint32_t free_ram   = mcu_free_ram();

    PickResult p = pick_model(budget_us, free_flash, free_ram);

    if (p.status != PICK_OK) {
        // НЕ беремо нишком найменший — кажемо ГОЛОСНО, що саме не так.
        switch (p.status) {
        case PICK_NONE_FITS_TIME:
            log_error("Vision: навіть найменший не вкладається в %lu мкс — "
                      "залегкий чип або задерганий дедлайн", (unsigned long)budget_us);
            break;
        case PICK_NONE_FITS_MEM:
            log_error("Vision: моделі досить швидкі, але не лізуть: "
                      "Flash=%lu B, RAM=%lu B", (unsigned long)free_flash,
                      (unsigned long)free_ram);
            break;
        default:
            log_error("Vision: таблиця моделей порожня");
            break;
        }
        return false;                        // ← стоп: апарат не злетить осліп
    }

    log_info("Vision: обрано варіант %s (mAP %u.%02u, виміряно %lu мкс/кадр)",
             p.chosen->name, p.chosen->map_x100 / 100, p.chosen->map_x100 % 100,
             (unsigned long)p.chosen->latency_us);

    // Віддаємо обрану модель у TFLite-харнес — він розкладе арену й перевірить її.
    return model_init(p.chosen->model_data, p.chosen->arena_bytes);
}
