/* Концептуальний вигляд швидкого шляху KCSAN */
static __always_inline void kcsan_check_access(const volatile void *ptr, size_t size, int type)
{
    /* 1. Якщо KCSAN глобально вимкнено для поточного потоку — негайне повернення */
    if (this_cpu_read(kcsan_ctx.disable_count))
        return;

    /* 2. Перевірка лічильника семплювання */
    if (unlikely(!kcsan_sample_counter_decrement())) {
        /* Лише 1 із N доступів потрапляє у повільний шлях встановлення watchpoint */
        kcsan_setup_watchpoint(ptr, size, type);
        return;
    }

    /* 3. Швидка перевірка: чи не встановлено watchpoint НА ЦЮ АДРЕСУ іншим потоком */
    if (unlikely(kcsan_is_watchpoint_active(ptr, size))) {
        kcsan_report_race(ptr, size, type);
    }
}
