#include <iostream>
#include <string_view>
#include <vector>
#include <functional>
#include <span>
#include <optional>

class NdjsonStreamParser {
public:
    explicit NdjsonStreamParser(size_t max_buffer_size = 65536)
        : max_size_(max_buffer_size) {
        buffer_.reserve(max_buffer_size);
    }

    /* Приймає порцію байтів і викликає обробник для кожного знайденого рядка JSON */
    template <typename Callback>
    bool feed(std::span<const char> chunk, Callback&& on_record) {
        if (buffer_.size() + chunk.size() > max_size_) {
            return false; /* Захист від неконтрольованого росту буфера */
        }

        buffer_.insert(buffer_.end(), chunk.begin(), chunk.end());
        size_t processed_offset = 0;

        for (size_t i = 0; i < buffer_.size(); ++i) {
            if (buffer_[i] == '\n') {
                size_t line_len = i - processed_offset;

                if (line_len > 0 && buffer_[processed_offset + line_len - 1] == '\r') {
                    --line_len;
                }

                if (line_len > 0) {
                    std::string_view record(buffer_.data() + processed_offset, line_len);
                    on_record(record);
                }

                processed_offset = i + 1;
            }
        }

        if (processed_offset > 0) {
            buffer_.erase(buffer_.begin(), buffer_.begin() + processed_offset);
        }

        return true;
    }

    /* Скидання залишкового запису в разі відсутності кінцевого переведення рядка */
    template <typename Callback>
    void flush(Callback&& on_record) {
        if (!buffer_.empty()) {
            size_t len = buffer_.size();
            if (buffer_[len - 1] == '\r') {
                --len;
            }
            if (len > 0) {
                on_record(std::string_view(buffer_.data(), len));
            }
            buffer_.clear();
        }
    }

private:
    size_t max_size_;
    std::vector<char> buffer_;
};

int main() {
    NdjsonStreamParser parser;
    int counter = 0;

    auto handle_record = [&counter](std::string_view line) {
        ++counter;
        std::cout << "[" << counter << "] Отримано запис: " << line << "\n";
    };

    const std::string_view p1 = "{\"sensor\":\"temp\",\"v\":21.5}\n{\"sensor\":\"press\",\"v\":101";
    const std::string_view p2 = ".3}\r\n{\"sensor\":\"hum\",\"v\":55.0}\n";

    parser.feed(std::span<const char>(p1.data(), p1.size()), handle_record);
    parser.feed(std::span<const char>(p2.data(), p2.size()), handle_record);
    parser.flush(handle_record);

    return 0;
}
