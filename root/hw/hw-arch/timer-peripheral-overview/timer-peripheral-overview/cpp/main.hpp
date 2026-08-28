// Час, зроблений із коду: блокує потік або ядро
gpio::set(servo_pin, true);
delay_microseconds(1500);
gpio::set(servo_pin, false);

// Час, зроблений із таймера через RAII-канал порівняння:
// апаратура генерує імпульс автономно у фоні
timer::channel_oc pwm_chan{TIM2, channel::ch1};
pwm_chan.set_period_ticks(19999);   // 20 мс при 1 МГц
pwm_chan.set_compare_ticks(1499);   // 1500 мкс імпульс
pwm_chan.enable();
