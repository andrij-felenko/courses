typedef enum {
    DISP_OFF,        // живлення знято, панель мертва
    DISP_INIT,       // холодний старт у процесі (паузи, насоси)
    DISP_ACTIVE,     // повний показ
    DISP_IDLE,       // приглушено, чекаємо на подію
    DISP_SLEEP       // sleep-in: насоси стоять, ~нуль струму
} disp_state_t;

static disp_state_t disp_state = DISP_OFF;   // ← явний стан, єдине джерело правди

// малювати дозволено ЛИШЕ в показових станах — інакше пишемо в панель, що не готова
bool display_ready(void) {
    return disp_state == DISP_ACTIVE || disp_state == DISP_IDLE;
}

void display_draw(const frame_t *f) {
    if (!display_ready()) return;   // захист: у INIT/SLEEP/OFF малювати марно або шкідливо
    framebuffer_blit(f);
}
