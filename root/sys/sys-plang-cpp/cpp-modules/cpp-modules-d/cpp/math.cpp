// Файл: math.cpp (Одиниця реалізації)
module math;

// Імпорт внутрішнього розділу для внутрішніх потреб
import :internals;

namespace math {
Vector3 add(Vector3 a, Vector3 b) {
    if (detail::is_nearly_zero(a.x)) { /* ... */ }
    return {a.x + b.x, a.y + b.y, a.z + b.z};
}
}
