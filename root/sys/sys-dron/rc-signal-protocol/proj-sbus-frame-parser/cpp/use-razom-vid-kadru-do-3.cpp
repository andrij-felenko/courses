sbus_data_t sb;
int ch_us[16];

if (sbus_read(&sb, ch_us)) {
    if (sb.failsafe) {
        enter_failsafe();               // утримати/повернутись/заглушити — за політикою апарата
    } else {
        apply_throttle(ch_us[2]);       // напр., газ на 3-му каналі, вже в мкс
        // frame_lost можна врахувати як «підозрілий кадр», але не як тривогу
    }
}
