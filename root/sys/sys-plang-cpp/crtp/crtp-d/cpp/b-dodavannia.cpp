template <typename Derived>
class InstanceCounter {
public:
    InstanceCounter() { ++live_count_; }
    InstanceCounter(const InstanceCounter&) { ++live_count_; }
    ~InstanceCounter() { --live_count_; }

    static size_t get_live_count() { return live_count_; }

private:
    inline static size_t live_count_{0};
};

class Texture : public InstanceCounter<Texture> {};
class Sound : public InstanceCounter<Sound> {};
