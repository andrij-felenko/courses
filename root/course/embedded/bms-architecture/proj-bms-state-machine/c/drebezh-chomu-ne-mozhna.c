#define CONFIRM_N   8u    // стільки однакових зчитувань поспіль = «вірю»

// Підтверджена тривога: повертає true лише коли небезпека протрималась N разів.
static bool alarm_confirmed(void)
{
    if (!safety_ok()) {
        if (bms.confirm_cnt < CONFIRM_N) bms.confirm_cnt++;
    } else {
        bms.confirm_cnt = 0;          // одне «норма» скидає лічильник
    }
    return (bms.confirm_cnt >= CONFIRM_N);
}
