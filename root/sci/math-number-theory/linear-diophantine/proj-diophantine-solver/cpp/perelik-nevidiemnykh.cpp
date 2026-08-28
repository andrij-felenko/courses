ll floordiv(ll a, ll b) { ll q = a / b; if (a % b && a < 0) q--; return q; }  // b>0
ll ceildiv (ll a, ll b) { ll q = a / b; if (a % b && a > 0) q++; return q; }  // b>0

// -1 → нескінченно багато; 0 → жодного (або a=b=0); >0 → перелік у out
int nonneg(ll a, ll b, ll c, std::vector<std::pair<ll,ll>> &out) {
    Sol s = solve(a, b, c);
    if (s.kind != 2) return 0;
    bool haveLo = false, haveHi = false; ll lo = 0, hi = 0;
    ll co[2] = { s.sx, s.sy }, ba[2] = { s.x, s.y };
    for (int i = 0; i < 2; i++) {
        ll coef = co[i], base = ba[i];
        if (coef == 0) { if (base < 0) return 0; continue; }   // координата фіксована й від'ємна
        if (coef > 0) { ll v = ceildiv(-base, coef);           // t ≥ ⌈−base/coef⌉
                        lo = haveLo ? std::max(lo, v) : v; haveLo = true; }
        else          { ll v = floordiv(base, -coef);          // t ≤ ⌊base/(−coef)⌋
                        hi = haveHi ? std::min(hi, v) : v; haveHi = true; }
    }
    if (!haveLo || !haveHi) return -1;                         // вікно відкрите з одного боку
    for (ll t = lo; t <= hi; t++)
        out.push_back({ s.x + s.sx * t, s.y + s.sy * t });
    return (int)out.size();
}
