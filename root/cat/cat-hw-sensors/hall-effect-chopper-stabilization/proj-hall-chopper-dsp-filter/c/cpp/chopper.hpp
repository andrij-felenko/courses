#pragma once

#include <cstdint>
#include <array>
#include <cstddef>

template<size_t Size>
class MovingAverage {
public:
    MovingAverage() : head_(0), sum_(0) {
        buffer_.fill(0);
    }

    int32_t process(int32_t new_val) {
        sum_ -= buffer_[head_];
        buffer_[head_] = new_val;
        sum_ += new_val;
        head_ = (head_ + 1) % Size;
        return sum_ / static_cast<int32_t>(Size);
    }

private:
    std::array<int32_t, Size> buffer_;
    size_t head_;
    int32_t sum_;
};

template<size_t Taps>
class FirFilter {
public:
    explicit FirFilter(const std::array<int32_t, Taps>& coeffs) 
        : coeffs_(coeffs), index_(0) {
        history_.fill(0);
    }

    int32_t process(int32_t new_val) {
        history_[index_] = new_val;
        int32_t out = 0;
        
        for (size_t i = 0; i < Taps; ++i) {
            size_t idx = (index_ + Taps - i) % Taps;
            out += history_[idx] * coeffs_[i];
        }
        
        index_ = (index_ + 1) % Taps;
        return out >> 10;
    }

private:
    std::array<int32_t, Taps> history_;
    std::array<int32_t, Taps> coeffs_;
    size_t index_;
};

class ChopperProcessor {
public:
    ChopperProcessor();
    int32_t process(int32_t phase0_val, int32_t phase1_val);

private:
    MovingAverage<16> ma_;
    FirFilter<4> fir_;
};
