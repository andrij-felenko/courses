// ── Пороги тривоги з гістерезисом ──
#define ALARM_ON   0.75f   // margin вище цього → тривога УВІМК (близько до межі)
#define ALARM_OFF  0.60f   // margin нижче цього → тривога ВИМК (відійшли)

static bool alarm = false;

// Оновити стан тривоги за поточним запасом (двопороговий гістерезис).
static void alarm_update(float margin) {
    if (!alarm && margin >= ALARM_ON)  alarm = true;   // ступили в небезпеку
    if ( alarm && margin <= ALARM_OFF) alarm = false;  // впевнено відійшли
    // у смузі 0.60..0.75 стан НЕ міняється — тут і живе гістерезис
}
