class AudioFilter {
public:
    explicit AudioFilter(int sample_rate) : m_sample_rate(sample_rate) {}
    virtual ~AudioFilter() = default;

    // Чисті віртуальні методи: клас більше не має реалізації за замовчуванням
    virtual void process(float* buffer, std::size_t frames) = 0;
    virtual double get_latency_ms() const = 0;

protected:
    int m_sample_rate;
};
