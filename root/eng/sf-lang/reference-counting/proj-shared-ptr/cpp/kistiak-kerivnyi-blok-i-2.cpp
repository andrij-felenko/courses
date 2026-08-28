template <class T>
class Shared {
    ControlBlock<T>* cb_ = nullptr;

    // приватний ctor: приймає блок ЯК Є (strong уже піднято тим, хто кличе)
    explicit Shared(ControlBlock<T>* cb) : cb_(cb) {}
    friend class Weak<T>;                    // Weak::lock будує Shared із блока

public:
    Shared() = default;                      // порожній покажчик

    // взяти сирий об'єкт під нагляд: створити блок, стати єдиним власником
    explicit Shared(T* raw)
        : cb_(raw ? new ControlBlock<T>(raw) : nullptr) {}

    T* get() const { return cb_ ? cb_->obj : nullptr; }
    T* operator->() const { return cb_->obj; }
    T& operator*()  const { return *cb_->obj; }
    long use_count() const { return cb_ ? cb_->strong : 0; }
    explicit operator bool() const { return cb_ && cb_->obj; }
};
