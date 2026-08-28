# SBUS: байт 23 кадру містить прапорці стану
SBUS_FLAG_FRAME_LOST = 1 << 5   # 0x20: окремий кадр загублено
SBUS_FLAG_FAILSAFE   = 1 << 4   # 0x10: приймач у режимі failsafe

# повертає True, якщо контролер мусить вмикати польотний failsafe
def rc_link_lost(flags: int) -> bool:
    if flags & SBUS_FLAG_FAILSAFE:   return True    # явна втрата зв'язку
    if flags & SBUS_FLAG_FRAME_LOST: return False   # один поганий кадр — ще не втрата
    return False                                    # усе гаразд

# flags = 0x10:
#   0x10 & SBUS_FLAG_FAILSAFE  = 0x10 → істина  → rc_link_lost() == True
#   → контролер запускає свою дію failsafe (RTL / посадку)
