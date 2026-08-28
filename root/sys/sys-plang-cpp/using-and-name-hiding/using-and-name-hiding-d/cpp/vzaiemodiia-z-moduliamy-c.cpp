export module MathEngine;

namespace internal {
    export struct Vector3D { double x, y, z; };
    export Vector3D add(Vector3D a, Vector3D b);
}

// Експортуємо функціонал у відкритий кореневий простір модуля:
export using internal::Vector3D;
export using internal::add;
