enum Dir { DIR_NONE, DIR_N, DIR_NE, DIR_E, DIR_SE,
           DIR_S, DIR_SW, DIR_W, DIR_NW };

// Звести вісь до знака −1/0/+1 за порогом (частка від повного ходу).
int sign3(int v, int threshold = 40) {
    if (v >  threshold) return  1;
    if (v < -threshold) return -1;
    return 0;
}

Dir readDir() {
    int hx = sign3(readAxis(horizontal));   // −1, 0, +1  (захід … схід)
    int hy = sign3(readAxis(vertical));     // −1, 0, +1  (південь … північ)

    if (hx == 0 && hy == 0) return DIR_NONE;

    // 3×3 → напрямок; вважаємо +Y = північ (вгору), +X = схід (вправо)
    if (hy ==  1) return (hx == -1) ? DIR_NW : (hx == 1) ? DIR_NE : DIR_N;
    if (hy == -1) return (hx == -1) ? DIR_SW : (hx == 1) ? DIR_SE : DIR_S;
    return (hx == -1) ? DIR_W : DIR_E;      // hy == 0, hx ≠ 0
}
