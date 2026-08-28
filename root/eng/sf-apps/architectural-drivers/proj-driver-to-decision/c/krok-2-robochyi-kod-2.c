// ── Фон. Усе НЕкритичне за часом. Може підвисати — не зачепить безпеку. ──
void main_loop(void)
{
    for (;;) {
        display_update_temperature(read_temp());  // вимога (A): неспішно
        comms_poll();                              // обмін з пультом

        if (fault_latched) {
            log_fault();                           // журнал — коли встигнеться
            show_fault_banner();                   // червоний банер на екран
        }
    }
}
