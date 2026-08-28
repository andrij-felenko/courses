class Widget {
    struct Impl;
    std::unique_ptr<Impl> pImpl_;

    Impl* get_impl() noexcept { return pImpl_.get(); }
    const Impl* get_impl() const noexcept { return pImpl_.get(); }

public:
    void render() const {
        // get_impl()->internal_counter_++; // ПОМИЛКА КОМПІЛЯЦІЇ: об'єкт константний!
    }
};
