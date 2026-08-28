#include <iostream>
#include <string_view>
#include <array>
#include <vector>
#include <span>
#include <cstdint>
#include <cstring>
#include <unistd.h>

class HorspoolMatcher {
public:
    explicit HorspoolMatcher(std::string_view pattern)
        : pattern_(pattern), pattern_len_(pattern.size()) {
        shift_table_.fill(pattern_len_);

        if (pattern_len_ > 0) {
            for (size_t i = 0; i < pattern_len_ - 1; ++i) {
                auto byte_val = static_cast<uint8_t>(pattern_[i]);
                shift_table_[byte_val] = pattern_len_ - 1 - i;
            }
        }
    }

    [[nodiscard]] bool contains_in(std::string_view text) const noexcept {
        if (pattern_len_ == 0) return true;
        if (text.size() < pattern_len_) return false;

        size_t i = pattern_len_ - 1;
        while (i < text.size()) {
            size_t k = 0;
            while (k < pattern_len_ && pattern_[pattern_len_ - 1 - k] == text[i - k]) {
                ++k;
            }
            if (k == pattern_len_) {
                return true;
            }
            auto bad_byte = static_cast<uint8_t>(text[i]);
            i += shift_table_[bad_byte];
        }
        return false;
    }

private:
    std::string_view pattern_;
    size_t pattern_len_{0};
    std::array<size_t, 256> shift_table_{};
};

class StreamProcessor {
public:
    static constexpr size_t BufferCapacity = 64 * 1024;

    explicit StreamProcessor(const HorspoolMatcher& matcher) noexcept
        : matcher_(matcher) {}

    int process_descriptor(int fd) {
        std::vector<char> buffer(BufferCapacity + 1);
        size_t carryover = 0;
        bool any_match = false;

        while (true) {
            ssize_t bytes_read = ::read(fd, buffer.data() + carryover, BufferCapacity - carryover);
            if (bytes_read < 0) {
                std::perror("read");
                return 2;
            }
            if (bytes_read == 0 && carryover == 0) {
                break;
            }

            size_t total_in_buffer = carryover + static_cast<size_t>(bytes_read);
            size_t line_start = 0;

            while (line_start < total_in_buffer) {
                auto* start_ptr = buffer.data() + line_start;
                size_t remaining = total_in_buffer - line_start;
                auto* newline_ptr = static_cast<char*>(std::memchr(start_ptr, '\n', remaining));

                if (!newline_ptr) {
                    if (bytes_read == 0) {
                        std::string_view last_line(start_ptr, remaining);
                        if (matcher_.contains_in(last_line)) {
                            [[maybe_unused]] auto w1 = ::write(STDOUT_FILENO, last_line.data(), last_line.size());
                            [[maybe_unused]] auto w2 = ::write(STDOUT_FILENO, "\n", 1);
                            any_match = true;
                        }
                        line_start = total_in_buffer;
                    }
                    break;
                }

                size_t line_end = static_cast<size_t>(newline_ptr - buffer.data());
                size_t line_len = line_end - line_start;
                std::string_view line_view(start_ptr, line_len);

                if (matcher_.contains_in(line_view)) {
                    [[maybe_unused]] auto w = ::write(STDOUT_FILENO, start_ptr, line_len + 1);
                    any_match = true;
                }

                line_start = line_end + 1;
            }

            carryover = total_in_buffer - line_start;
            if (carryover > 0) {
                std::memmove(buffer.data(), buffer.data() + line_start, carryover);
            }

            if (carryover == BufferCapacity) {
                std::string_view overflow_line(buffer.data(), carryover);
                if (matcher_.contains_in(overflow_line)) {
                    [[maybe_unused]] auto w1 = ::write(STDOUT_FILENO, overflow_line.data(), overflow_line.size());
                    [[maybe_unused]] auto w2 = ::write(STDOUT_FILENO, "\n", 1);
                    any_match = true;
                }
                carryover = 0;
            }

            if (bytes_read == 0) {
                break;
            }
        }

        return any_match ? 0 : 1;
    }

private:
    const HorspoolMatcher& matcher_;
};

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: mini_grep <шаблон>\n";
        return 2;
    }

    HorspoolMatcher matcher(argv[1]);
    StreamProcessor processor(matcher);
    return processor.process_descriptor(STDIN_FILENO);
}
