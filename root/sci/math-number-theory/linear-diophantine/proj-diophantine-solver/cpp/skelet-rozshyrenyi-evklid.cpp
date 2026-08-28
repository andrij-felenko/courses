#include <vector>
#include <algorithm>
using ll = long long;

// a·x + b·y = НСД(a, b); повертає сам НСД, пише x, y
ll ext_gcd(ll a, ll b, ll &x, ll &y) {
    ll r0 = a, r1 = b, s0 = 1, s1 = 0, t0 = 0, t1 = 1;
    while (r1 != 0) {
        ll q = r0 / r1;
        ll r = r0 - q * r1; r0 = r1; r1 = r;   // остача Евкліда
        ll s = s0 - q * s1; s0 = s1; s1 = s;   // коефіцієнт при a
        ll t = t0 - q * t1; t0 = t1; t1 = t;   // коефіцієнт при b
    }
    x = s0; y = t0;
    return r0;                                 // a·s0 + b·t0 == r0 == НСД
}
