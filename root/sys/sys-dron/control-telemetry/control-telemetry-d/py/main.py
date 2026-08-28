RC_TIMEOUT_MS = 500   # 0.5 с без валідного кадру = втрата

# викликається з основного циклу польотного контролера (~раз на такт)
def rc_failsafe_tick(now_ms):
    if now_ms - g_last_rc_frame_ms > RC_TIMEOUT_MS:
        enter_failsafe(FS_RTL)            # повернення додому (RTL)

# приймач: щойно прийшов валідний кадр керування — оновлюємо мітку часу
def on_rc_frame_valid(now_ms):
    global g_last_rc_frame_ms
    g_last_rc_frame_ms = now_ms
