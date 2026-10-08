template <size_t N>
class SignalFilter {
private:
    uint16_t buffer_[N];
    size_t head_ = 0;
    size_t count_ = 0;

public:
    SignalFilter() {
        memset(buffer_, 0, sizeof(buffer_));
    }

    uint16_t process(uint16_t sample) {
        buffer_[head_] = sample;
        head_ = (head_ + 1) % N;
        if (count_ < N) count_++;

        uint16_t sorted[N];
        memcpy(sorted, buffer_, count_ * sizeof(uint16_t));
        for (size_t i = 0; i < count_ - 1; ++i) {
            for (size_t j = i + 1; j < count_; ++j) {
                if (sorted[i] > sorted[j]) {
                    uint16_t tmp = sorted[i];
                    sorted[i] = sorted[j];
                    sorted[j] = tmp;
                }
            }
        }
        return sorted[count_ / 2];
    }
};
