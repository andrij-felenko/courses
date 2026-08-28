#include <vector>
#include <string>
#include <algorithm>
#include <cstring>

class GapBuffer {
public:
    explicit GapBuffer(size_t initial_capacity = 64)
        : buffer_(std::max<size_t>(initial_capacity, 16)),
          gap_start_(0),
          gap_end_(buffer_.size()) {}

    void insert(char c) {
        if (gap_start_ == gap_end_) {
            grow();
        }
        buffer_[gap_start_++] = c;
    }

    void move_cursor(size_t new_pos) {
        if (new_pos < gap_start_) {
            const size_t delta = gap_start_ - new_pos;
            std::memmove(&buffer_[gap_end_ - delta], &buffer_[new_pos], delta);
            gap_start_ -= delta;
            gap_end_ -= delta;
        } else if (new_pos > gap_start_) {
            const size_t delta = new_pos - gap_start_;
            std::memmove(&buffer_[gap_start_], &buffer_[gap_end_], delta);
            gap_start_ += delta;
            gap_end_ += delta;
        }
    }

    [[nodiscard]] size_t size() const noexcept {
        return buffer_.size() - (gap_end_ - gap_start_);
    }

private:
    std::vector<char> buffer_;
    size_t gap_start_;
    size_t gap_end_;

    void grow() {
        const size_t old_cap = buffer_.size();
        const size_t new_cap = old_cap * 2;
        const size_t post_gap_len = old_cap - gap_end_;
        const size_t new_gap_end = new_cap - post_gap_len;

        std::vector<char> new_buffer(new_cap);
        std::memcpy(new_buffer.data(), buffer_.data(), gap_start_);
        std::memcpy(new_buffer.data() + new_gap_end, buffer_.data() + gap_end_, post_gap_len);

        buffer_ = std::move(new_buffer);
        gap_end_ = new_gap_end;
    }
};
