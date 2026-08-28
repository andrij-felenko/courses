// ldpc_codec.hpp — Ідіоматична C++20 обгортка для бібліотеки libldpc
#pragma once

#include <span>
#include <vector>
#include <string>
#include <memory>
#include <optional>
#include <expected>
#include <cstdint>

namespace ldpc {

enum class Algorithm : std::uint8_t {
    SumProduct        = 0,
    MinSum            = 1,
    NormalizedMinSum  = 2,
    OffsetMinSum      = 3
};

enum class Status : std::int8_t {
    Success                  =  0,
    ErrorMaxIterations       = -1,
    ErrorInvalidParam        = -2,
    ErrorInvalidMatrix       = -3,
    ErrorOutOfMemory         = -4,
    ErrorBufferTooSmall      = -5
};

struct Config {
    std::size_t num_v{0};
    std::size_t num_c{0};
    std::vector<std::uint8_t> h_matrix;
    
    Algorithm algo{Algorithm::NormalizedMinSum};
    std::uint32_t max_iterations{50};
    float norm_factor{0.8f};
    float offset_factor{0.15f};
    float llr_clip_val{20.0f};
};

struct DecodeResult {
    std::vector<std::uint8_t> bits;
    std::uint32_t iterations_used{0};
};

class Codec {
public:
    // Фабричний метод створення об'єкта кодека через std::expected
    [[nodiscard]] static std::expected<Codec, Status> create(const Config& config);

    Codec(Codec&&) noexcept = default;
    Codec& operator=(Codec&&) noexcept = default;

    Codec(const Codec&) = delete;
    Codec& operator=(const Codec&) = delete;

    ~Codec() = default;

    // Метод кодування систематичного блоку
    [[nodiscard]] std::expected<std::vector<std::uint8_t>, Status> encode(
        std::span<const std::uint8_t> info_bits) const;

    // Метод ітеративного декодування LLR
    [[nodiscard]] std::expected<DecodeResult, Status> decode(
        std::span<const float> channel_llr) const;

    // Динамічне оновлення конфігурації
    Status set_parameters(Algorithm algo, std::uint32_t max_iterations) noexcept;

    [[nodiscard]] std::size_t codeword_length() const noexcept { return num_v_; }
    [[nodiscard]] std::size_t parity_length() const noexcept { return num_c_; }
    [[nodiscard]] std::size_t info_length() const noexcept { return num_v_ - num_c_; }

private:
    explicit Codec(const Config& config);

    std::size_t num_v_{0};
    std::size_t num_c_{0};
    Config config_;
    
    class Impl;
    std::unique_ptr<Impl> impl_; // Pimpl ідіома для збереження ABI
};

[[nodiscard]] inline std::string to_string(Status status) {
    switch (status) {
        case Status::Success: return "Success";
        case Status::ErrorMaxIterations: return "Max iterations reached without syndrome convergence";
        case Status::ErrorInvalidParam: return "Invalid input parameters or nullptr";
        case Status::ErrorInvalidMatrix: return "Invalid sparse parity-check H matrix";
        case Status::ErrorOutOfMemory: return "Out of memory allocation error";
        case Status::ErrorBufferTooSmall: return "Output buffer is too small";
        default: return "Unknown status code";
    }
}

} // namespace ldpc
