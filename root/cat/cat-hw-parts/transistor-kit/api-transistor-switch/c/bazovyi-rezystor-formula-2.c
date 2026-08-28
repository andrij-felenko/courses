// Скільки струму втече в базу при заданому Rb — і чи стерпить це вивід МК.
float base_current(float rb, float v_gpio) {
    return (v_gpio - 0.7f) / rb;    // струм бази, А
}

bool gpio_can_drive(float rb, float v_gpio, float pin_limit) {
    return base_current(rb, v_gpio) <= pin_limit;  // pin_limit ≈ 0.020…0.040 А
}
// При Rb = 470 Ом і 3.3 В: i_base = 2.6/470 ≈ 5.5 мА — виводу легко (стеля ~20 мА).
// А от Rb = 100 Ом дав би 26 мА — уже НЕБЕЗПЕЧНО для типового піна.
