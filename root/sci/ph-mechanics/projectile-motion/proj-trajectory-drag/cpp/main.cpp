#include <cmath>

struct State { double x, y, vx, vy; };
constexpr double g = 9.81;

// похідна стану: прискорення від тяжіння + квадратичного опору
static State accel(State s, double k) {
    double sp = std::hypot(s.vx, s.vy);       // |v| зчіплює осі
    return { s.vx, s.vy, -k*sp*s.vx, -g - k*sp*s.vy };
}
static State axpy(State s, State d, double h) {  // s + h·d покомпонентно
    return { s.x + h*d.x, s.y + h*d.y, s.vx + h*d.vx, s.vy + h*d.vy };
}
static State rk4_step(State s, double k, double dt) {
    State k1 = accel(s, k);                    // нахил на старті
    State k2 = accel(axpy(s, k1, dt/2), k);    // …на пробному півкроці
    State k3 = accel(axpy(s, k2, dt/2), k);    // …ще раз посередині
    State k4 = accel(axpy(s, k3, dt), k);      // …у кінці кроку
    auto mix = [&](double a, double b, double c, double d) {
        return dt/6 * (a + 2*b + 2*c + d);     // зважене середнє
    };
    return { s.x  + mix(k1.x, k2.x, k3.x, k4.x),
             s.y  + mix(k1.y, k2.y, k3.y, k4.y),
             s.vx + mix(k1.vx, k2.vx, k3.vx, k4.vx),
             s.vy + mix(k1.vy, k2.vy, k3.vy, k4.vy) };
}
