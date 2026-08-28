struct Sol { int kind; ll x, y, sx, sy, d; };   // kind: 0 нема · 1 уся площина · 2 родина

Sol solve(ll a, ll b, ll c) {
    if (a == 0 && b == 0)                        // ліва частина завжди 0
        return { c == 0 ? 1 : 0, 0, 0, 0, 0, 0 };
    ll x0, y0, g = ext_gcd(a, b, x0, y0);
    if (g < 0) { g = -g; x0 = -x0; y0 = -y0; }   // НСД → додатний, знак на коефіцієнти
    if (c % g != 0)                              // критерій: d мусить ділити c
        return { 0, 0, 0, 0, 0, 0 };
    ll k = c / g;
    ll x1 = x0 * k, y1 = y0 * k;                 // ⚠ можливе переповнення (див. пастки)
    ll sx = b / g, sy = -(a / g);                // крок родини (b/d, −a/d)
    if (sx != 0) {                               // звести перший розв'язок до найменшого |x|
        ll m = sx < 0 ? -sx : sx;
        ll xr = ((x1 % m) + m) % m;              // C++ % буває від'ємним — нормуємо в [0, m)
        ll t = (xr - x1) / sx; x1 = xr; y1 += sy * t;
    } else {                                     // b = 0: x зафіксований, зводимо y
        ll m = sy < 0 ? -sy : sy;
        ll yr = ((y1 % m) + m) % m;
        ll t = (yr - y1) / sy; y1 = yr; x1 += sx * t;
    }
    return { 2, x1, y1, sx, sy, g };
}
