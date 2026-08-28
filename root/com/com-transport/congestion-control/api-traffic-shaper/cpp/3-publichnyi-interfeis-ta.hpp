#ifndef TRAFFIC_SHAPER_HPP
#define TRAFFIC_SHAPER_HPP

#include <cstdint>
#include <cstddef>
#include <vector>
#include <chrono>
#include <optional>
#include <stdexcept>

enum class ShaperMode {
    Shape,
    Police,
    Mark
};

enum class ShaperResult {
    Ok,
    Queued,
    DropFull,
    DropPolicing
};

struct ShaperConfig {
    std::uint64_t cir_bytes_per_sec;
    std::uint64_t cbs_bytes;
    std::size_t max_queue_bytes{64 * 1024};
    ShaperMode mode{ShaperMode::Shape};
};

class TokenBucketShaper {
public:
    explicit TokenBucketShaper(const ShaperConfig& config)
        : config_(config),
          tokens_bytes_(static_cast<double>(config.cbs_bytes)),
          current_queue_bytes_(0),
          last_update_us_(0) {
        if (config.cir_bytes_per_sec == 0 || config.cbs_bytes == 0) {
            throw std::invalid_argument("CIR та CBS повинні бути більше 0");
        }
    }

    void update_tokens(std::uint64_t now_us) {
        if (last_update_us_ == 0) {
            last_update_us_ = now_us;
            return;
        }

        std::uint64_t elapsed_us = now_us - last_update_us_;
        last_update_us_ = now_us;

        double added_tokens = (static_cast<double>(elapsed_us) * config_.cir_bytes_per_sec) / 1000000.0;
        tokens_bytes_ += added_tokens;

        if (tokens_bytes_ > static_cast<double>(config_.cbs_bytes)) {
            tokens_bytes_ = static_cast<double>(config_.cbs_bytes);
        }
    }

    ShaperResult process_packet(std::size_t packet_len_bytes, std::uint64_t now_us) {
        update_tokens(now_us);

        double len = static_cast<double>(packet_len_bytes);

        if (tokens_bytes_ >= len) {
            tokens_bytes_ -= len;
            return ShaperResult::Ok;
        }

        if (config_.mode == ShaperMode::Police) {
            return ShaperResult::DropPolicing;
        }

        if (current_queue_bytes_ + packet_len_bytes > config_.max_queue_bytes) {
            return ShaperResult::DropFull;
        }

        current_queue_bytes_ += packet_len_bytes;
        return ShaperResult::Queued;
    }

    std::uint64_t get_wait_time_us(std::size_t packet_len_bytes, std::uint64_t now_us) {
        update_tokens(now_us);

        if (tokens_bytes_ >= static_cast<double>(packet_len_bytes)) {
            return 0;
        }

        double needed = static_cast<double>(packet_len_bytes) - tokens_bytes_;
        double wait_seconds = needed / static_cast<double>(config_.cir_bytes_per_sec);
        return static_cast<std::uint64_t>(wait_seconds * 1000000.0);
    }

    double get_tokens() const noexcept {
        return tokens_bytes_;
    }

private:
    ShaperConfig config_;
    double tokens_bytes_;
    std::size_t current_queue_bytes_;
    std::uint64_t last_update_us_;
};

#endif // TRAFFIC_SHAPER_HPP
