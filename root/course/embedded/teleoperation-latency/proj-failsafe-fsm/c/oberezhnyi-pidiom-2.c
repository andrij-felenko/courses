// Скільки ударів поспіль ми пропустили = тиша / період серцебиття.
// За цим числом визначаємо, на яку сходинку тривоги слід піднятися.
static fs_state_t fs_target_state(uint32_t silent_ms, uint32_t hb_period_ms)
{
    if (hb_period_ms == 0u) hb_period_ms = 100u;   // захист від ділення на нуль
    uint32_t missed = silent_ms / hb_period_ms;    // цілих пропущених ударів

    if (missed >= BEATS_TO_RTL)   return FS_RTL;
    if (missed >= BEATS_TO_STOP)  return FS_SAFE_STOP;
    if (missed >= BEATS_TO_HOLD)  return FS_HOLD;
    return FS_NORMAL;
}
