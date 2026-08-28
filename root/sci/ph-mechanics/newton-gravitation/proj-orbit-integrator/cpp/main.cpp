// гарячий цикл: тісно, без алокацій — так рахують N-тіл насправді
#include <cmath>
struct Body { double x, y, vx, vy; };
constexpr double GM = 1.0;

static inline void accel(double x, double y, double& ax, double& ay) {
    double r2 = x*x + y*y;
    double inv = -GM / (r2 * std::sqrt(r2));  // −GM / r³
    ax = inv*x;  ay = inv*y;
}

static inline void verlet_step(Body& b, double dt) {
    double ax, ay;  accel(b.x, b.y, ax, ay);
    b.x += b.vx*dt + 0.5*ax*dt*dt;            // дрейф
    b.y += b.vy*dt + 0.5*ay*dt*dt;
    double ax2, ay2;  accel(b.x, b.y, ax2, ay2);  // сила в новій точці
    b.vx += 0.5*(ax + ax2)*dt;                // швидкість — середнім прискоренням
    b.vy += 0.5*(ay + ay2)*dt;
}

int main() {
    Body b{1.0, 0.0, 0.0, 1.2};
    for (long i = 0; i < 100'000'000L; ++i)   // сто мільйонів кроків
        verlet_step(b, 0.01);
}
