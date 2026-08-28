template <typename Derived>
class ShapeInterface {
public:
    void draw() const {
        // Статичний поліморфізм: виклик методу конкретного спадкоємця без vtable!
        static_cast<const Derived*>(this)->draw_impl();
    }
};

class Circle : public ShapeInterface<Circle> {
public:
    void draw_impl() const {
        std::cout << "Малювання кола\n";
    }
};
