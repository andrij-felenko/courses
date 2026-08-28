class Widget {
    struct Impl;
    std::unique_ptr<Impl> pImpl_;
public:
    void render() const {
        // Компілятор ДОЗВОЛЯЄ цей рядок, хоча метод const!
        pImpl_->internal_counter_++; 
        pImpl_->clear_cache();
    }
};
