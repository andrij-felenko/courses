// Концептуальна реалізація паттерну Concept/Model
template <typename R, typename... Args>
class ConceptModelFunction {
private:
    struct Concept {
        virtual ~Concept() = default;
        virtual R invoke(Args... args) = 0;
    };

    template <typename F>
    struct Model : Concept {
        F functor_;
        Model(F f) : functor_(std::move(f)) {}
        R invoke(Args... args) override {
            return functor_(args...);
        }
    };

    std::unique_ptr<Concept> pimpl_;

public:
    template <typename F>
    ConceptModelFunction(F f) 
        : pimpl_(std::make_unique<Model<F>>(std::move(f))) {}

    R operator()(Args... args) const {
        return pimpl_->invoke(args...);
    }
};
