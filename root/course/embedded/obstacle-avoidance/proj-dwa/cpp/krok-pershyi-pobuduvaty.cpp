typedef struct {
    float v_lo, v_hi;   // межі поступальної швидкості у вікні
    float w_lo, w_hi;   // межі поворотної швидкості у вікні
} Window;

// Динамічне вікно Vd навколо поточного стану, обрізане стелею Vs.
Window dynamic_window(float v0, float w0)
{
    Window win;

    // Vd: за такт DT прискорення дає ±a·DT від поточної швидкості.
    win.v_lo = v0 - A_BRAKE * DT;     // униз — на скільки встигнемо загальмувати
    win.v_hi = v0 + A_ACC   * DT;     // вгору — на скільки встигнемо розігнатися
    win.w_lo = w0 - AL_BRAKE * DT;
    win.w_hi = w0 + AL_ACC   * DT;

    // Vs: обрізаємо стелею заліза (швидше/крутіше апарат не вміє).
    if (win.v_lo < V_MIN) win.v_lo = V_MIN;
    if (win.v_hi > V_MAX) win.v_hi = V_MAX;
    if (win.w_lo < -W_MAX) win.w_lo = -W_MAX;
    if (win.w_hi >  W_MAX) win.w_hi =  W_MAX;

    return win;
}
