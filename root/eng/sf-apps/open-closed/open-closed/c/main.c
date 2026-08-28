typedef enum { CIRCLE, RECT, TRIANGLE } ShapeKind;

typedef struct {
    ShapeKind kind;
    double a, b;            // радіус / сторони / основа й висота
} Shape;

double area(const Shape *s) {
    switch (s->kind) {
        case CIRCLE:   return 3.14159265 * s->a * s->a;
        case RECT:     return s->a * s->b;
        case TRIANGLE: return 0.5 * s->a * s->b;
        // кожна нова фігура — нова гілка ТУТ, у вже працюючій функції
    }
    return 0.0;
}
