template <typename Derived>
class Builder {
public:
    Derived& reset() {
        Derived& self = *static_cast<Derived*>(this);
        self.clear_state();
        return self;
    }

    const Derived& inspect() const {
        const Derived& self = *static_cast<const Derived*>(this);
        self.print_debug();
        return self;
    }
};
