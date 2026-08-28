struct Vec2 {
    float x, y;
    Vec2  operator+(Vec2 o) const { return {x + o.x, y + o.y}; }
    Vec2  operator-(Vec2 o) const { return {x - o.x, y - o.y}; }
    Vec2  operator*(float s) const { return {x * s, y * s}; }
    float dot(Vec2 o)       const { return x * o.x + y * o.y; }
};

struct Body {
    Vec2  pos, vel;
    float invMass;                        // 0 = нерухома стіна (нескінченна маса)
};

// n — одинична нормаль від b до a; depth — глибина проникання.
void resolveContact(Body& a, Body& b, Vec2 n, float depth, float e) {
    const float invSum = a.invMass + b.invMass;
    if (invSum == 0.0f) return;                       // дві стіни — нема кого рухати

    const float vn = (a.vel - b.vel).dot(n);          // швидкість зближення
    if (vn > 0.0f) return;                            // уже розходяться — не чіпати

    const float eEff = (vn > -1.0f) ? 0.0f : e;       // поріг проти дрижання спокою
    const float j    = -(1.0f + eEff) * vn / invSum;  // скалярний поштовх
    const Vec2  P    = n * j;                         // вектор поштовху
    a.vel = a.vel + P * a.invMass;
    b.vel = b.vel - P * b.invMass;

    const float slop = 0.01f, beta = 0.2f;            // позиційна корекція
    const float corr = (depth - slop > 0.0f ? depth - slop : 0.0f) / invSum * beta;
    const Vec2  C    = n * corr;
    a.pos = a.pos + C * a.invMass;
    b.pos = b.pos - C * b.invMass;
}
