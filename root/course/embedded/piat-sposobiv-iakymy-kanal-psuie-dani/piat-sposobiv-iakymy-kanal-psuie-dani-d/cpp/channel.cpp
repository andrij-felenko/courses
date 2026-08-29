#include "channel.hpp"

#include <algorithm>

bool Channel::roll(unsigned permille) {
    std::uniform_int_distribution<unsigned> dist(0, 999);
    return dist(rng_) < permille;
}

// Завада тривалістю кількасот мікросекунд б'є не один біт, а пачку сусідніх.
void Channel::corrupt_burst(std::span<std::uint8_t> data) {
    const std::size_t total_bits = data.size() * 8;
    if (total_bits == 0) {
        return;
    }
    std::uniform_int_distribution<std::size_t> start_dist(0, total_bits - 1);
    std::uniform_int_distribution<unsigned>    width_dist(3, 10);

    const std::size_t start = start_dist(rng_);
    const unsigned    width = width_dist(rng_);

    for (unsigned i = 0; i < width; ++i) {
        const std::size_t bit = start + i;
        if (bit >= total_bits) {
            break;
        }
        data[bit / 8] ^= static_cast<std::uint8_t>(0x80 >> (bit % 8));
    }
}

void Channel::push(link::Bytes bytes) {
    if (stream_len_ + bytes.size() > kStreamCap) {
        ++stats_.overflow;   // черга лінії переповнена — байти гинуть, як у FIFO UART
        return;
    }
    for (std::size_t i = 0; i < bytes.size(); ++i) {
        stream_[(stream_head_ + stream_len_ + i) % kStreamCap] = bytes[i];
    }
    stream_len_ += bytes.size();
}

void Channel::send(link::Bytes frame) {
    ++stats_.offered;
    if (frame.empty() || frame.size() > link::kMaxWire) {
        return;
    }

    if (roll(profile_.drop_permille)) {
        ++stats_.dropped;
    } else {
        Packet packet;
        packet.len = frame.size();
        std::ranges::copy(frame, packet.bytes.begin());
        const std::span<std::uint8_t> body{packet.bytes.data(), packet.len};

        if (roll(profile_.burst_permille)) {
            corrupt_burst(body);
            ++stats_.corrupted;
        }

        if (!held_ && roll(profile_.reorder_permille)) {
            // Кадр пішов довшим маршрутом: віддамо його після наступного.
            held_ = packet;
            ++stats_.reordered;
            return;
        }

        push(body);
        if (roll(profile_.duplicate_permille)) {
            push(body);
            ++stats_.duplicated;
        }
    }

    if (held_) {
        push(link::Bytes{held_->bytes.data(), held_->len});
        held_.reset();
    }
}

void Channel::pump(const link::ByteSink& sink) {
    if (stream_len_ == 0) {
        if (held_) {
            // Нових кадрів немає — випускаємо затриманий, щоб не завис назавжди.
            push(link::Bytes{held_->bytes.data(), held_->len});
            held_.reset();
        }
        return;
    }

    std::uniform_int_distribution<std::size_t> chunk_dist(1, kMaxChunk);
    const std::size_t chunk = std::min(chunk_dist(rng_), stream_len_);

    std::array<std::uint8_t, kMaxChunk> buffer{};
    for (std::size_t i = 0; i < chunk; ++i) {
        buffer[i] = stream_[(stream_head_ + i) % kStreamCap];
    }
    stream_head_ = (stream_head_ + chunk) % kStreamCap;
    stream_len_ -= chunk;

    // Шматок може розрізати кадр посередині або принести півтора кадру відразу.
    sink(link::Bytes{buffer.data(), chunk});
}
