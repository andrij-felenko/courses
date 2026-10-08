template <uint8_t N>
class MovingAverageFilter {
public:
    MovingAverageFilter() : index_(0), count_(0), sum_(0.0f) {}

    float update(float input) {
        if (count_ < N) {
            buffer_[index_] = input;
            sum_ += input;
            count_++;
        } else {
            sum_ -= buffer_[index_];
            buffer_[index_] = input;
            sum_ += input;
        }
        index_ = (index_ + 1) % N;
        return sum_ / static_cast<float>(count_);
    }

private:
    float buffer_[N];
    uint8_t index_;
    uint8_t count_;
    float sum_;
};

class ExponentialFilter {
public:
    explicit ExponentialFilter(float alpha = 0.1f)
        : alpha_((alpha > 0.0f && alpha <= 1.0f) ? alpha : 0.1f),
          filtered_value_(0.0f),
          initialized_(false) {}

    float update(float input) {
        if (!initialized_) {
            filtered_value_ = input;
            initialized_ = true;
        } else {
            filtered_value_ = (alpha_ * input) + ((1.0f - alpha_) * filtered_value_);
        }
        return filtered_value_;
    }

private:
    float alpha_;
    float filtered_value_;
    bool initialized_;
};
