class Chart : public std::enable_shared_from_this<Chart> {
public:
    // …
    void attach(EventBus& bus) {
        std::weak_ptr<Chart> weak = weak_from_this();
        sub_ = bus.connect([weak](const Tick& ev) {
            if (std::shared_ptr<Chart> live = weak.lock())
                live->push(ev.value);
        });
    }
private:
    std::vector<double> data_;
    Subscription sub_;      // ~Chart зніме слот
};
