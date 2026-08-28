// Інвертуючий підсилювач: рахуємо очікуваний вихід за номіналами.
// Так прошивка переводить виміряний Vout назад у Vin (і навпаки).
float invert_gain(float r_in, float r_f) {
    return -(r_f / r_in);              // Vout/Vin = −Rf/Rin
}

float expected_vout(float v_in, float r_in, float r_f) {
    return invert_gain(r_in, r_f) * v_in;
}

// Rin = 1 кОм, Rf = 10 кОм  →  підсилення −10
// Vin = +0.5 В  →  Vout = −5.0 В
