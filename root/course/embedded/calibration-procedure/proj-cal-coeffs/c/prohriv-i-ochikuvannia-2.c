static void wait_low_step(uint32_t t)
{
    if (op_pressed_capture()) {
        avg_begin(t);
        cal.state = CAL_AVG_LOW;
        ui_prompt("Знімаю нижню опору, не чіпайте...");
    }
}

static void wait_high_step(uint32_t t)
{
    if (op_pressed_capture()) {
        avg_begin(t);
        cal.state = CAL_AVG_HIGH;
        ui_prompt("Знімаю верхню опору, не чіпайте...");
    }
}
