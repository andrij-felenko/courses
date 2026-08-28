/* АНТИПАТЕРН: формальна інкапсуляція без приховування інформації */
class TelemetryEngine {
public:
    // Ґеттери й сеттери повністю виказують структуру та розмір буфера
    void set_raw_samples(const std::vector<float> &s) { raw_samples_ = s; }
    [[nodiscard]] const std::vector<float>& get_raw_samples() const noexcept { return raw_samples_; }

    void set_head_index(size_t h) { head_ = h; }
    [[nodiscard]] size_t get_head_index() const noexcept { return head_; }

private:
    std::vector<float> raw_samples_; // Таємниця витекла через сигнатури методів!
    size_t head_{0};
};
