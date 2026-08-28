#include <iostream>
#include <string>
#include <string_view>
#include <span>
#include <functional>
#include <vector>
#include <cstdint>

enum class MultipartState {
    Start,
    StartBoundary,
    HeaderField,
    HeaderValue,
    HeadersAlmostDone,
    PartData,
    BoundaryMatch,
    End
};

struct MultipartCallbacks {
    std::function<void()> on_part_begin;
    std::function<void(std::string_view name, std::string_view value)> on_header;
    std::function<void(std::span<const uint8_t> chunk)> on_part_data;
    std::function<void()> on_part_end;
};

class StreamingMultipartParser {
public:
    explicit StreamingMultipartParser(std::string_view boundary, MultipartCallbacks callbacks)
        : callbacks_(std::move(callbacks)),
          boundary_("--" + std::string(boundary)),
          state_(MultipartState::Start),
          match_index_(0) {}

    void execute(std::span<const uint8_t> buffer) {
        size_t mark = 0;

        for (size_t i = 0; i < buffer.size(); ++i) {
            const uint8_t byte = buffer[i];

            switch (state_) {
            case MultipartState::Start:
            case MultipartState::StartBoundary:
                if (byte == static_cast<uint8_t>(boundary_[match_index_])) {
                    if (++match_index_ == boundary_.size()) {
                        match_index_ = 0;
                        state_ = MultipartState::HeadersAlmostDone;
                        if (callbacks_.on_part_begin) callbacks_.on_part_begin();
                    }
                } else {
                    match_index_ = 0;
                }
                break;

            case MultipartState::HeadersAlmostDone:
                if (byte == '\n') {
                    state_ = MultipartState::HeaderField;
                    header_name_.clear();
                    header_value_.clear();
                }
                break;

            case MultipartState::HeaderField:
                if (byte == '\r') {
                    // Очікуємо переведення рядка
                } else if (byte == '\n') {
                    state_ = MultipartState::PartData;
                    mark = i + 1;
                } else if (byte == ':') {
                    state_ = MultipartState::HeaderValue;
                } else {
                    header_name_.push_back(static_cast<char>(byte));
                }
                break;

            case MultipartState::HeaderValue:
                if (byte == '\r') {
                    // Очікуємо переведення рядка
                } else if (byte == '\n') {
                    if (callbacks_.on_header) {
                        callbacks_.on_header(header_name_, header_value_);
                    }
                    header_name_.clear();
                    header_value_.clear();
                    state_ = MultipartState::HeaderField;
                } else if (byte != ' ' || !header_value_.empty()) {
                    header_value_.push_back(static_cast<char>(byte));
                }
                break;

            case MultipartState::PartData:
                if (byte == '\r') {
                    if (i > mark && callbacks_.on_part_data) {
                        callbacks_.on_part_data(buffer.subspan(mark, i - mark));
                    }
                    state_ = MultipartState::BoundaryMatch;
                    match_index_ = 0;
                }
                break;

            case MultipartState::BoundaryMatch:
                if (match_index_ == 0 && byte == '\n') {
                    match_index_ = 1;
                } else if (match_index_ >= 1 && (match_index_ - 1) < boundary_.size() &&
                           byte == static_cast<uint8_t>(boundary_[match_index_ - 1])) {
                    match_index_++;
                    if ((match_index_ - 1) == boundary_.size()) {
                        if (callbacks_.on_part_end) callbacks_.on_part_end();
                        state_ = MultipartState::HeadersAlmostDone;
                        match_index_ = 0;
                    }
                } else {
                    // Відкат помилкового збігу межі у двійковому вмісті
                    if (callbacks_.on_part_data) {
                        const uint8_t cr = '\r';
                        callbacks_.on_part_data(std::span<const uint8_t>(&cr, 1));
                        if (match_index_ > 1) {
                            const uint8_t lf = '\n';
                            callbacks_.on_part_data(std::span<const uint8_t>(&lf, 1));
                            auto bspan = std::span<const uint8_t>(
                                reinterpret_cast<const uint8_t*>(boundary_.data()), match_index_ - 2);
                            callbacks_.on_part_data(bspan);
                        }
                    }
                    state_ = MultipartState::PartData;
                    mark = i;
                    i--; // Повторно обробляємо поточний байт
                }
                break;

            case MultipartState::End:
                return;
            }
        }

        if (state_ == MultipartState::PartData && buffer.size() > mark) {
            if (callbacks_.on_part_data) {
                callbacks_.on_part_data(buffer.subspan(mark, buffer.size() - mark));
            }
        }
    }

private:
    MultipartCallbacks callbacks_;
    std::string boundary_;
    MultipartState state_;
    size_t match_index_;
    std::string header_name_;
    std::string header_value_;
};
