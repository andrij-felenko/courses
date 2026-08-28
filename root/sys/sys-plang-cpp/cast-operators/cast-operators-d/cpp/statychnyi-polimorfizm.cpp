template <typename Derived>
class ShapeCRTP {
public:
    void draw() const {
        // Статичний downcast без жодного оверхеду vtable та RTTI:
        static_cast<const Derived*>(this)->draw_impl();
    }
};

class CircleCRTP : public ShapeCRTP<CircleCRTP> {
public:
    void draw_impl() const {
        // Конкретна реалізація малювання кола
    }
};

template <typename T>
void render_shape(const ShapeCRTP<T>& shape) {
    shape.draw(); // Прямий виклик функції без vtable lookup (inlined!)
}
