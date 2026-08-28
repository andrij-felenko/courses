template <typename Derived>
class StaticAudioFilter {
public:
    void process(float* buffer, std::size_t frames) {
        // Статичний NVI-каркас: нуль накладних витрат у рантаймі
        static_cast<Derived*>(this)->process_impl(buffer, frames);
    }
};

class FastLowPass : public StaticAudioFilter<FastLowPass> {
public:
    void process_impl(float* buffer, std::size_t frames) {
        // Прямий виклик: компілятор повністю вбудовує цей код!
        for (std::size_t i = 0; i < frames; ++i) buffer[i] *= 0.5f;
    }
};
