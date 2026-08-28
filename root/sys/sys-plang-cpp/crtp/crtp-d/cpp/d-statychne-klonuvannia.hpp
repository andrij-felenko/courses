#include <memory>

template <typename Derived>
class Cloneable {
public:
    std::unique_ptr<Derived> clone() const {
        const auto& self = *static_cast<const Derived*>(this);
        return std::make_unique<Derived>(self);
    }
};

class GameEntity : public Cloneable<GameEntity> {
public:
    int health{100};
    int mana{50};
};
