// вхід:  v — лінійна швидкість, м/с; w — кутова швидкість, рад/с
//        b — піввідстань між колесами, м; v_max — стеля колеса, м/с
// вихід: vl, vr — швидкості лівого й правого коліс, |·| ≤ v_max
void diff_drive_mix(float v, float w, float b, float v_max,
                    float *vl, float *vr)
{
    // 1) сирий розклад: спільне v обом, різниця w·b — на розворот
    float turn = w * b;
    float left  = v - turn;
    float right = v + turn;

    // 2) чи не пробило котресь колесо стелю (за модулем)?
    float mag = fabsf(left) > fabsf(right) ? fabsf(left) : fabsf(right);

    // 3) нормування: якщо пробило — стиснути ОБИДВА в одній пропорції,
    //    щоб зберегти їхнє відношення (тобто розворот), а не обрізати одне
    if (mag > v_max) {
        float scale = v_max / mag;   // < 1
        left  *= scale;
        right *= scale;
    }

    *vl = left;
    *vr = right;
}
