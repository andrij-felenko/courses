// opus_demo.cpp - RAII обгортка та безпечний C++20 інтерфейс для libopus
#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <stdexcept>
#include <string_view>
#include <opus/opus.h>

namespace opus {

class OpusException : public std::runtime_error {
public:
    explicit OpusException(int error_code)
        : std::runtime_error(opus_strerror(error_code)), code_(error_code) {}

    [[nodiscard]] int code() const noexcept { return code_; }
private:
    int code_;
};

struct EncoderDeleter {
    void operator()(OpusEncoder* enc) const noexcept {
        if (enc) opus_encoder_destroy(enc);
    }
};

struct DecoderDeleter {
    void operator()(OpusDecoder* dec) const noexcept {
        if (dec) opus_decoder_destroy(dec);
    }
};

class Encoder {
public:
    Encoder(int sample_rate, int channels, int application) {
        int err = OPUS_OK;
        encoder_.reset(opus_encoder_create(sample_rate, channels, application, &err));
        if (err != OPUS_OK) {
            throw OpusException(err);
        }
    }

    void set_bitrate(int bitrate_bps) {
        int err = opus_encoder_ctl(encoder_.get(), OPUS_SET_BITRATE(bitrate_bps));
        if (err != OPUS_OK) throw OpusException(err);
    }

    void set_inband_fec(bool enable) {
        int err = opus_encoder_ctl(encoder_.get(), OPUS_SET_INBAND_FEC(enable ? 1 : 0));
        if (err != OPUS_OK) throw OpusException(err);
    }

    [[nodiscard]] size_t encode(std::span<const int16_t> pcm_input, std::span<uint8_t> packet_output) {
        opus_int32 res = opus_encode(
            encoder_.get(),
            pcm_input.data(),
            static_cast<int>(pcm_input.size()),
            packet_output.data(),
            static_cast<opus_int32>(packet_output.size())
        );
        if (res < 0) {
            throw OpusException(res);
        }
        return static_cast<size_t>(res);
    }

private:
    std::unique_ptr<OpusEncoder, EncoderDeleter> encoder_;
};

class Decoder {
public:
    Decoder(int sample_rate, int channels) {
        int err = OPUS_OK;
        decoder_.reset(opus_decoder_create(sample_rate, channels, &err));
        if (err != OPUS_OK) {
            throw OpusException(err);
        }
    }

    [[nodiscard]] size_t decode(std::span<const uint8_t> packet_input, std::span<int16_t> pcm_output, bool decode_fec = false) {
        int res = opus_decode(
            decoder_.get(),
            packet_input.data(),
            static_cast<opus_int32>(packet_input.size()),
            pcm_output.data(),
            static_cast<int>(pcm_output.size()),
            decode_fec ? 1 : 0
        );
        if (res < 0) {
            throw OpusException(res);
        }
        return static_cast<size_t>(res);
    }

private:
    std::unique_ptr<OpusDecoder, DecoderDeleter> decoder_;
};

} // namespace opus

int main() {
    try {
        constexpr int sample_rate = 48000;
        constexpr int channels = 1;
        constexpr size_t frame_size = 960; // 20 ms

        opus::Encoder encoder(sample_rate, channels, OPUS_APPLICATION_VOIP);
        encoder.set_bitrate(32000);
        encoder.set_inband_fec(true);

        opus::Decoder decoder(sample_rate, channels);

        std::vector<int16_t> pcm_in(frame_size, 1000);
        std::vector<uint8_t> opus_packet(1500);
        std::vector<int16_t> pcm_out(frame_size);

        size_t bytes = encoder.encode(pcm_in, opus_packet);
        std::cout << "C++ Opus Wrapper: Encoded " << bytes << " bytes.\n";

        size_t samples = decoder.decode(std::span(opus_packet.data(), bytes), pcm_out);
        std::cout << "C++ Opus Wrapper: Decoded " << samples << " samples.\n";

    } catch (const opus::OpusException& e) {
        std::cerr << "Opus Error: " << e.what() << " (code " << e.code() << ")\n";
        return 1;
    }

    return 0;
}
