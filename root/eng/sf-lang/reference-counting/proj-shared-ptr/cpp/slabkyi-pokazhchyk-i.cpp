template <class T>
class Weak {
    ControlBlock<T>* cb_ = nullptr;

public:
    Weak() = default;

    Weak(const Shared<T>& s) : cb_(s.cb_) {  // почати спостерігати за тим, чим володіє s
        if (cb_) cb_->weak_retain();          // +1 до СЛАБКОГО лічильника
    }
    Weak(const Weak& o) : cb_(o.cb_) {
        if (cb_) cb_->weak_retain();
    }
    Weak& operator=(const Weak& o) {
        if (o.cb_) o.cb_->weak_retain();      // той самий порядок: захопити до звільнити
        if (cb_)   cb_->weak_release();
        cb_ = o.cb_;
        return *this;
    }
    ~Weak() { if (cb_) cb_->weak_release(); }

    bool expired() const { return !cb_ || cb_->strong == 0; }

    Shared<T> lock() const {
        if (cb_ && cb_->strong != 0) {        // об'єкт іще живий?
            cb_->retain();                     // застовпити ще одне СИЛЬНЕ посилання
            return Shared<T>(cb_);             // приватний ctor: блок уже з піднятим strong
        }
        return Shared<T>();                    // порожньо — об'єкта вже нема
    }
};
