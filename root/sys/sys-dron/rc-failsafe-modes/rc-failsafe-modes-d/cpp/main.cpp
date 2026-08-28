// SBUS: байт 23 кадру містить прапорці стану
#define SBUS_FLAG_FRAME_LOST  (1u << 5)   // 0x20: окремий кадр загублено
#define SBUS_FLAG_FAILSAFE    (1u << 4)   // 0x10: приймач у режимі failsafe

// повертає true, якщо контролер мусить вмикати польотний failsafe
bool rc_link_lost(uint8_t flags) {
    if (flags & SBUS_FLAG_FAILSAFE)   return true;   // явна втрата зв'язку
    if (flags & SBUS_FLAG_FRAME_LOST) return false;  // один поганий кадр — ще не втрата
    return false;                                    // усе гаразд
}

// flags = 0x10:
//   0x10 & SBUS_FLAG_FAILSAFE  = 0x10 → істина  → rc_link_lost() == true
//   → контролер запускає свою дію failsafe (RTL / посадку)
