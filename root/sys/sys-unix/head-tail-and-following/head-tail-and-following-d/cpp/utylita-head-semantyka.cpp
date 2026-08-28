#include <iostream>
#include <vector>
#include <span>
#include <cstring>
#include <unistd.h>

class StreamHead {
public:
    explicit StreamHead(size_t max_lines) noexcept : max_lines_{max_lines} {}

    void process(int fd_in) {
        std::vector<char> buffer(8192);
        size_t lines_count = 0;
        ssize_t bytes_read = 0;

        while (lines_count < max_lines_ && 
              (bytes_read = ::read(fd_in, buffer.data(), buffer.size())) > 0) {
            
            std::span<const char> chunk{buffer.data(), static_cast<size_t>(bytes_read)};
            size_t offset = 0;

            while (lines_count < max_lines_ && offset < chunk.size()) {
                const void* found = std::memchr(chunk.data() + offset, '\n', chunk.size() - offset);
                if (!found) {
                    // Виводимо залишок буфера
                    auto remaining = chunk.subspan(offset);
                    if (::write(STDOUT_FILENO, remaining.data(), remaining.size()) < 0) {
                        return;
                    }
                    break;
                }

                auto nl_ptr = static_cast<const char*>(found);
                size_t line_len = (nl_ptr - (chunk.data() + offset)) + 1;
                auto slice = chunk.subspan(offset, line_len);

                if (::write(STDOUT_FILENO, slice.data(), slice.size()) < 0) {
                    return;
                }

                offset += line_len;
                ++lines_count;
            }
        }
    }

private:
    size_t max_lines_;
};

int main(int argc, char* argv[]) {
    size_t lines = (argc > 1) ? std::stoul(argv[1]) : 10;
    StreamHead head{lines};
    head.process(STDIN_FILENO);
    return 0;
}
