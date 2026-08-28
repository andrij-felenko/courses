class Chart : public std::enable_shared_from_this<Chart> {
public:
    static std::shared_ptr<Chart> create() { return std::shared_ptr<Chart>(new Chart); }

    void attach(EventBus& bus) {
        std::weak_ptr<Chart> weak = weak_from_this();
        bus.subscribe([weak](const Tick& ev) {
            if (std::shared_ptr<Chart> live = weak.lock())
                live->push(ev.value);
        });
    }

    void push(double v) { data_.push_back(v); }

private:
    Chart() = default;
    std::vector<double> data_;
};
