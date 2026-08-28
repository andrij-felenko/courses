// Напрям обертання конкретного гвинта — фізичний факт, не вподобання.
typedef enum { PROP_CCW = +1, PROP_CW = -1 } PropSpin;

// Коефіцієнт рискання ВИВОДИТЬСЯ з напряму гвинта, а не вбивається вручну.
// Так неможливо випадково розійтися зі знаком реактивного моменту.
static float yaw_coeff(PropSpin spin) {
    // CCW-гвинт штовхає раму CW → додатна команда yaw має пришвидшити його.
    return (float)spin;   // PROP_CCW → +1, PROP_CW → −1
}

// Заповнити стовпець yaw матриці з фактичних напрямів моторів.
void build_yaw_column(const PropSpin spin[4], MixRow mix[4]) {
    for (int i = 0; i < 4; ++i)
        mix[i].yaw = yaw_coeff(spin[i]);
}
