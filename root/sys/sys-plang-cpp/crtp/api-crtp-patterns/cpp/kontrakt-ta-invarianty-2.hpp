#include <memory>

template <typename Derived>
class Cloneable {
public:
    std::unique_ptr<Derived> clone() const {
        const auto& self = *static_cast<const Derived*>(this);
        return std::make_unique<Derived>(self);
    }
};

class GraphicPrimitive : public Cloneable<GraphicPrimitive> {
public:
    int x{0};
    int y{0};
};
