volatile bool tick_due = false;
void TIMER_ISR(void) { tick_due = true; }     // коротко: лише відмітка

void control_loop_run(void) {
    for (;;) {
        if (tick_due) {
            tick_due = false;
            control_tick();                    // довга робота — поза ISR
        }
    }
}
