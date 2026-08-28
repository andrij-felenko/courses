// гарячий цикл рушія: по цій парі тисячі разів за кадр, без жодних алокацій
struct Body { double x, v, m, r; };

inline void resolve(Body* bodies, int i, int j, double e) {
    Body& a = bodies[i];
    Body& b = bodies[j];
    const double inv = 1.0 / (a.m + b.m);
    const double vcm = (a.m*a.v + b.m*b.v) * inv;   // швидкість центра мас
    a.v = (1 + e)*vcm - e*a.v;
    b.v = (1 + e)*vcm - e*b.v;
}
