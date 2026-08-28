// Синтаксичний парсер та формувальник повідомлень зі статичним буфером на C++20
#include <array>
#include <cstdint>
#include <cstring>
#include <expected>
#include <span>
#include <string_view>

namespace embedded::msg {

enum class ParseError : uint8_t {
    SyntaxError,
    BufferOverflow,
    UnclosedBrace,
    MissingOther
};

enum class NodeType : uint8_t {
    Text,
    Arg,
    Hash,
    Choice
};

struct Branch {
    std::string_view label{};
    uint16_t child_start{0};
    uint16_t child_count{0};
};

struct Node {
    NodeType type{NodeType::Text};
    std::string_view text{};
    bool is_plural{false};
    int32_t offset{0};
    uint16_t branch_start{0};
    uint16_t branch_count{0};
};

struct Argument {
    std::string_view name;
    std::string_view str_val{};
    int32_t num_val{0};
    bool is_numeric{false};
};

template <size_t MaxNodes = 32, size_t MaxBranches = 8>
class TemplateParser {
public:
    constexpr explicit TemplateParser(std::string_view src) noexcept : src_{src} {}

    [[nodiscard]] constexpr std::expected<uint16_t, ParseError> parse() noexcept {
        uint16_t count = 0;
        uint16_t start = parse_message(false, count);
        if (err_ != ParseError::SyntaxError && !has_error_) {
            return count;
        }
        return std::unexpected(err_);
    }

    [[nodiscard]] size_t evaluate(
        std::span<const Argument> args,
        std::string_view (*plural_fn)(int32_t),
        std::span<char> out_buf) const noexcept
    {
        size_t out_pos = 0;
        eval_range(0, root_count_, args, plural_fn, 0, out_buf, out_pos);
        if (out_pos < out_buf.size()) {
            out_buf[out_pos] = '\0';
        }
        return out_pos;
    }

private:
    std::string_view src_;
    size_t pos_{0};
    std::array<Node, MaxNodes> nodes_{};
    uint16_t node_count_{0};
    std::array<Branch, MaxBranches> branches_{};
    uint16_t branch_count_{0};
    uint16_t root_count_{0};
    ParseError err_{ParseError::SyntaxError};
    bool has_error_{false};

    constexpr void skip_whitespace() noexcept {
        while (pos_ < src_.size() && (src_[pos_] == ' ' || src_[pos_] == '\t' ||
                                      src_[pos_] == '\n' || src_[pos_] == '\r')) {
            ++pos_;
        }
    }

    constexpr std::string_view parse_ident() noexcept {
        skip_whitespace();
        size_t start = pos_;
        while (pos_ < src_.size()) {
            char c = src_[pos_];
            if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
                (c >= '0' && c <= '9') || c == '_' || c == '.' || c == '=') {
                ++pos_;
            } else {
                break;
            }
        }
        return src_.substr(start, pos_ - start);
    }

    constexpr uint16_t parse_choice() noexcept {
        ++pos_; /* Пропуск '{' */
        auto arg_name = parse_ident();
        skip_whitespace();

        if (pos_ < src_.size() && src_[pos_] == '}') {
            ++pos_;
            if (node_count_ >= MaxNodes) { set_err(ParseError::BufferOverflow); return 0; }
            uint16_t idx = node_count_++;
            nodes_[idx] = Node{ .type = NodeType::Arg, .text = arg_name };
            return idx;
        }

        if (pos_ >= src_.size() || src_[pos_] != ',') { set_err(ParseError::SyntaxError); return 0; }
        ++pos_;

        auto kind = parse_ident();
        bool is_plural = (kind == "plural");
        if (!is_plural && kind != "select") { set_err(ParseError::SyntaxError); return 0; }

        skip_whitespace();
        if (pos_ >= src_.size() || src_[pos_] != ',') { set_err(ParseError::SyntaxError); return 0; }
        ++pos_;

        if (node_count_ >= MaxNodes) { set_err(ParseError::BufferOverflow); return 0; }
        uint16_t choice_idx = node_count_++;
        uint16_t b_start = branch_count_;
        uint16_t b_count = 0;
        bool has_other = false;

        while (pos_ < src_.size() && src_[pos_] != '}') {
            skip_whitespace();
            if (pos_ < src_.size() && src_[pos_] == '}') break;

            auto label = parse_ident();
            if (label.empty()) { set_err(ParseError::SyntaxError); return choice_idx; }
            if (label == "other") has_other = true;

            skip_whitespace();
            if (pos_ >= src_.size() || src_[pos_] != '{') { set_err(ParseError::SyntaxError); return choice_idx; }
            ++pos_;

            if (branch_count_ >= MaxBranches) { set_err(ParseError::BufferOverflow); return choice_idx; }
            uint16_t b_idx = branch_count_++;
            ++b_count;

            uint16_t child_cnt = 0;
            uint16_t child_st = parse_message(true, child_cnt);
            branches_[b_idx] = Branch{ .label = label, .child_start = child_st, .child_count = child_cnt };

            if (pos_ >= src_.size() || src_[pos_] != '}') { set_err(ParseError::UnclosedBrace); return choice_idx; }
            ++pos_;
        }

        if (pos_ >= src_.size() || src_[pos_] != '}') { set_err(ParseError::UnclosedBrace); return choice_idx; }
        ++pos_;

        if (!has_other) { set_err(ParseError::MissingOther); }

        nodes_[choice_idx] = Node{
            .type = NodeType::Choice,
            .text = arg_name,
            .is_plural = is_plural,
            .offset = 0,
            .branch_start = b_start,
            .branch_count = b_count
        };
        return choice_idx;
    }

    constexpr uint16_t parse_message(bool in_branch, uint16_t &out_count) noexcept {
        uint16_t start_idx = node_count_;
        uint16_t count = 0;
        size_t txt_start = pos_;

        while (pos_ < src_.size() && !has_error_) {
            char c = src_[pos_];
            if (in_branch && c == '}') break;

            if (c == '{' || (in_branch && c == '#')) {
                if (pos_ > txt_start) {
                    if (node_count_ >= MaxNodes) { set_err(ParseError::BufferOverflow); break; }
                    nodes_[node_count_++] = Node{
                        .type = NodeType::Text,
                        .text = src_.substr(txt_start, pos_ - txt_start)
                    };
                    ++count;
                }
                if (c == '#') {
                    if (node_count_ >= MaxNodes) { set_err(ParseError::BufferOverflow); break; }
                    nodes_[node_count_++] = Node{ .type = NodeType::Hash };
                    ++count;
                    ++pos_;
                    txt_start = pos_;
                } else {
                    parse_choice();
                    ++count;
                    txt_start = pos_;
                }
            } else {
                ++pos_;
            }
        }
        if (pos_ > txt_start && !has_error_) {
            if (node_count_ < MaxNodes) {
                nodes_[node_count_++] = Node{
                    .type = NodeType::Text,
                    .text = src_.substr(txt_start, pos_ - txt_start)
                };
                ++count;
            }
        }
        out_count = count;
        if (!in_branch) root_count_ = count;
        return start_idx;
    }

    constexpr void set_err(ParseError e) noexcept {
        err_ = e;
        has_error_ = true;
    }

    void eval_range(uint16_t start, uint16_t count, std::span<const Argument> args,
                    std::string_view (*plural_fn)(int32_t), int32_t active_num,
                    std::span<char> out_buf, size_t &out_pos) const noexcept
    {
        for (uint16_t i = 0; i < count; ++i) {
            const auto &n = nodes_[start + i];
            if (n.type == NodeType::Text) {
                append_span(n.text, out_buf, out_pos);
            } else if (n.type == NodeType::Hash) {
                char num_buf[16];
                int nlen = std::snprintf(num_buf, sizeof(num_buf), "%d", active_num);
                append_span(std::string_view(num_buf, static_cast<size_t>(nlen)), out_buf, out_pos);
            } else if (n.type == NodeType::Arg) {
                for (const auto &a : args) {
                    if (a.name == n.text) {
                        if (a.is_numeric) {
                            char num_buf[16];
                            int nlen = std::snprintf(num_buf, sizeof(num_buf), "%d", a.num_val);
                            append_span(std::string_view(num_buf, static_cast<size_t>(nlen)), out_buf, out_pos);
                        } else {
                            append_span(a.str_val, out_buf, out_pos);
                        }
                        break;
                    }
                }
            } else if (n.type == NodeType::Choice) {
                std::string_view matched_lbl = "other";
                int32_t next_num = active_num;
                for (const auto &a : args) {
                    if (a.name == n.text) {
                        if (n.is_plural && a.is_numeric) {
                            next_num = a.num_val;
                            matched_lbl = plural_fn ? plural_fn(next_num) : "other";
                        } else if (!n.is_plural && !a.is_numeric) {
                            matched_lbl = a.str_val;
                        }
                        break;
                    }
                }
                uint16_t sel_idx = 0;
                for (uint16_t b = 0; b < n.branch_count; ++b) {
                    const auto &br = branches_[n.branch_start + b];
                    if (br.label == matched_lbl) { sel_idx = b; break; }
                    if (br.label == "other") sel_idx = b;
                }
                const auto &chosen = branches_[n.branch_start + sel_idx];
                eval_range(chosen.child_start, chosen.child_count, args, plural_fn, next_num, out_buf, out_pos);
            }
        }
    }

    static void append_span(std::string_view s, std::span<char> buf, size_t &pos) noexcept {
        if (pos >= buf.size()) return;
        size_t avail = buf.size() - pos - 1;
        size_t n = s.size() < avail ? s.size() : avail;
        std::memcpy(buf.data() + pos, s.data(), n);
        pos += n;
    }
};

} // namespace embedded::msg
