// Єдина точка переходів: тут — увесь порядок і всі паузи, більше ніде.
void display_request(disp_event_t ev) {
    switch (disp_state) {
    case DISP_OFF:
        if (ev == EV_WAKE)  { cold_start(); disp_state = DISP_ACTIVE; }
        break;
    case DISP_ACTIVE:
        if (ev == EV_TIMEOUT) { backlight_dim();  disp_state = DISP_IDLE;  }
        if (ev == EV_SLEEP)   { go_to_sleep();     disp_state = DISP_SLEEP; }
        break;
    case DISP_IDLE:
        if (ev == EV_TOUCH)   { backlight_full();  disp_state = DISP_ACTIVE; }
        if (ev == EV_TIMEOUT) { go_to_sleep();     disp_state = DISP_SLEEP;  }
        break;
    case DISP_SLEEP:
        if (ev == EV_TOUCH)   { wake_from_sleep(); disp_state = DISP_ACTIVE; }
        break;
    default: break;   // у DISP_INIT події ігноруємо — старт завершиться сам
    }
}
