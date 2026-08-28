#pragma once
#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <string_view>
#include <expected>
#include <memory>

#ifdef _WIN32
  #define BRIDGE_API __declspec(dllexport)
#else
  #define BRIDGE_API __attribute__((visibility("default")))
#endif

extern "C" {

enum class BridgeStatus : int32_t {
    Ok = 0,
    ErrNullPtr = 1,
    ErrInvalidParam = 2,
    ErrOutOfMemory = 3,
    ErrComputation = 4
};

struct alignas(8) BridgeConfig {
    int32_t sample_rate;
    int32_t channels;
    double  scale_factor;
    uint8_t enable_filter;
    uint8_t padding[7];
};

struct BridgeContext;

BRIDGE_API BridgeStatus bridge_create_context(const BridgeConfig *config, BridgeContext **out_ctx);
BRIDGE_API BridgeStatus bridge_process_buffer(BridgeContext *ctx, const float *input, size_t count, float **out_buf, size_t *out_count);
BRIDGE_API void         bridge_free_buffer(float *buf);
BRIDGE_API void         bridge_free_context(BridgeContext *ctx);
BRIDGE_API const char*  bridge_get_last_error(BridgeStatus status);

} // extern "C"

// Ідіоматичний C++23 RAII-клас для безпечного клієнтського використання
class SafeBridgeClient {
public:
    static std::expected<SafeBridgeClient, std::string_view> create(const BridgeConfig& cfg) {
        BridgeContext* raw_ctx = nullptr;
        BridgeStatus st = bridge_create_context(&cfg, &raw_ctx);
        if (st != BridgeStatus::Ok) {
            return std::unexpected(bridge_get_last_error(st));
        }
        return SafeBridgeClient(raw_ctx);
    }

    ~SafeBridgeClient() {
        if (ctx_) bridge_free_context(ctx_);
    }

    SafeBridgeClient(const SafeBridgeClient&) = delete;
    SafeBridgeClient& operator=(const SafeBridgeClient&) = delete;
    SafeBridgeClient(SafeBridgeClient&& o) noexcept : ctx_(std::exchange(o.ctx_, nullptr)) {}
    SafeBridgeClient& operator=(SafeBridgeClient&& o) noexcept {
        if (this != &o) {
            if (ctx_) bridge_free_context(ctx_);
            ctx_ = std::exchange(o.ctx_, nullptr);
        }
        return *this;
    }

    std::expected<std::vector<float>, std::string_view> process(std::span<const float> input) {
        float* out_raw = nullptr;
        size_t out_len = 0;
        BridgeStatus st = bridge_process_buffer(ctx_, input.data(), input.size(), &out_raw, &out_len);
        if (st != BridgeStatus::Ok) {
            return std::unexpected(bridge_get_last_error(st));
        }
        std::vector<float> result(out_raw, out_raw + out_len);
        bridge_free_buffer(out_raw);
        return result;
    }

private:
    explicit SafeBridgeClient(BridgeContext* ctx) : ctx_(ctx) {}
    BridgeContext* ctx_{nullptr};
};
