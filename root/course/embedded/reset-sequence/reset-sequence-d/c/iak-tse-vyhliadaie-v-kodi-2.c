// Те саме згортання вручну на Cortex-M, де гачка shutdown немає.

void graceful_reset(reset_reason_t why)
{
    // 1) Фізику — у безпеку (поки ще керуємо).
    motors_all_stop();
    heater_off();

    // 2) Зберегти критичний стан і дочекатися запису у флеш.
    state_save_critical();
    flash_wait_write_done();

    // 3) Згорнути звʼязок, 4) лишити слід.
    net_close_all_sockets();
    reboot_counter_increment();
    log_reset_reason(why);

    // 5) Flush усіх відкладених записів — і лише тоді тригер.
    __DSB();                 // дочекатись, поки памʼять справді дописалась
    NVIC_SystemReset();      // всередині теж DSB + AIRCR(0x5FA | SYSRESETREQ)
    for (;;) { }             // reset не миттєвий — більше нічого не робимо
}
