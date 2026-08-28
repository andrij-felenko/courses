void control_tick(void) {
    float y = read_temp();                 // вибірка виміру
    float e = setpoint - y;                // помилка

    // прямий зв'язок: потужність проти витоку тепла — з моделі, наперед
    float u_ff = k_loss * (setpoint - T_room);

    // зворотний зв'язок: ловить лишок — похибку моделі й збурення (протяг, кришка)
    float u_fb = controller_step(e);       // P, PI чи PID

    set_heater(clampf(u_ff + u_fb, 0.0f, U_MAX));  // сума двох гілок, з межею
}
