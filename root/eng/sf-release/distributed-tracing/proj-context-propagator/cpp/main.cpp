#include <array>
#include <string_view>
#include <optional>
#include <expected>
#include <cstdint>
#include <chrono>
#include <random>
#include <format>
#include <iostream>
#include <span>

enum class TraceError {
    InvalidLength,
    InvalidDelimiter,
    InvalidVersion,
    InvalidHexCharacter,
    AllZerosNotAllowed
};

struct TraceContext {
    uint8_t version{0x00};
    std::array<uint8_t, 16> trace_id{};
    std::array<uint8_t, 8> span_id{};
    uint8_t flags{0x00};

    [[nodiscard]] bool is_sampled() const noexcept {
        return (flags & 0x01) != 0;
    }
};

class W3CPropagator {
    static constexpr std::string_view HEX_DIGITS = "0123456789abcdef";

    static constexpr int8_t parse_nibble(char c) noexcept {
        if (c >= '0' && c <= '9') return static_cast<int8_t>(c - '0');
        if (c >= 'a' && c <= 'f') return static_cast<int8_t>(c - 'a' + 10);
        if (c >= 'A' && c <= 'F') return static_cast<int8_t>(c - 'A' + 10);
        return -1;
    }

    template <size_t N>
    static bool decode_hex_span(std::string_view sv, std::array<uint8_t, N>& out) noexcept {
        uint8_t non_zero_acc = 0;
        for (size_t i = 0; i < N; ++i) {
            int8_t hi = parse_nibble(sv[i * 2]);
            int8_t lo = parse_nibble(sv[i * 2 + 1]);
            if (hi < 0 || lo < 0) return false;
            out[i] = static_cast<uint8_t>((hi << 4) | lo);
            non_zero_acc |= out[i];
        }
        return non_zero_acc != 0; /* Перевірка на заборонений zero-only ID */
    }

public:
    static std::expected<TraceContext, TraceError> extract(std::string_view header) noexcept {
        if (header.size() < 55) {
            return std::unexpected(TraceError::InvalidLength);
        }

        if (header[2] != '-' || header[35] != '-' || header[52] != '-') {
            return std::unexpected(TraceError::InvalidDelimiter);
        }

        int8_t v_hi = parse_nibble(header[0]);
        int8_t v_lo = parse_nibble(header[1]);
        if (v_hi < 0 || v_lo < 0) return std::unexpected(TraceError::InvalidHexCharacter);
        
        uint8_t ver = static_cast<uint8_t>((v_hi << 4) | v_lo);
        if (ver == 0xFF) return std::unexpected(TraceError::InvalidVersion);
        if (ver == 0x00 && header.size() != 55) return std::unexpected(TraceError::InvalidLength);

        TraceContext ctx;
        ctx.version = ver;

        if (!decode_hex_span(header.substr(3, 32), ctx.trace_id)) {
            return std::unexpected(TraceError::AllZerosNotAllowed);
        }

        if (!decode_hex_span(header.substr(36, 16), ctx.span_id)) {
            return std::unexpected(TraceError::AllZerosNotAllowed);
        }

        int8_t f_hi = parse_nibble(header[53]);
        int8_t f_lo = parse_nibble(header[54]);
        if (f_hi < 0 || f_lo < 0) return std::unexpected(TraceError::InvalidHexCharacter);
        ctx.flags = static_cast<uint8_t>((f_hi << 4) | f_lo);

        return ctx;
    }

    static void inject(const TraceContext& ctx, std::span<char, 55> out_buffer) noexcept {
        auto* p = out_buffer.data();
        *p++ = HEX_DIGITS[(ctx.version >> 4) & 0x0F];
        *p++ = HEX_DIGITS[ctx.version & 0x0F];
        *p++ = '-';

        for (uint8_t b : ctx.trace_id) {
            *p++ = HEX_DIGITS[(b >> 4) & 0x0F];
            *p++ = HEX_DIGITS[b & 0x0F];
        }
        *p++ = '-';

        for (uint8_t b : ctx.span_id) {
            *p++ = HEX_DIGITS[(b >> 4) & 0x0F];
            *p++ = HEX_DIGITS[b & 0x0F];
        }
        *p++ = '-';

        *p++ = HEX_DIGITS[(ctx.flags >> 4) & 0x0F];
        *p++ = HEX_DIGITS[ctx.flags & 0x0F];
    }
};

/* RAII-обгортка для відстеження тривалості спана */
class ScopedSpan {
    std::string_view operation_name_;
    TraceContext context_;
    std::chrono::steady_clock::time_point start_time_;

public:
    ScopedSpan(std::string_view name, TraceContext parent_ctx)
        : operation_name_(name), context_(parent_ctx), start_time_(std::chrono::steady_clock::now()) {
        /* Генерація нового SpanID для поточної операції */
        static thread_local std::mt19937_64 rng{std::random_device{}()};
        uint64_t new_id = rng();
        for (size_t i = 0; i < 8; ++i) {
            context_.span_id[i] = static_cast<uint8_t>(new_id >> (i * 8));
        }
    }

    ~ScopedSpan() {
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::steady_clock::now() - start_time_
        ).count();
        std::cout << std::format("[SPAN END] op='{}' duration={}us sampled={}\n",
                                 operation_name_, duration, context_.is_sampled());
    }

    [[nodiscard]] const TraceContext& context() const noexcept { return context_; }
};
