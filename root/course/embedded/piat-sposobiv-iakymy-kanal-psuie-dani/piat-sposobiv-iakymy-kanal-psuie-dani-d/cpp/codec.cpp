#include "codec.hpp"

namespace link::codec {

std::expected<std::size_t, Error> cobs_encode(Bytes src, std::span<std::uint8_t> dst) noexcept {
    if (dst.empty()) {
        return std::unexpected(Error::NoSpace);
    }

    std::size_t read_i = 0;
    std::size_t code_i = 0;   // місце, зарезервоване під покажчик зміщення групи
    std::size_t write_i = 1;
    std::uint8_t code = 1;    // зміщення до наступного нуля, рахуючи сам покажчик

    while (read_i < src.size()) {
        if (src[read_i] == 0x00) {
            // Нуль не передається: він стає довжиною щойно закритої групи.
            dst[code_i] = code;
            code = 1;
            code_i = write_i++;
            if (code_i >= dst.size()) {
                return std::unexpected(Error::NoSpace);
            }
            ++read_i;
        } else {
            if (write_i >= dst.size()) {
                return std::unexpected(Error::NoSpace);
            }
            dst[write_i++] = src[read_i++];
            ++code;
            if (code == 0xFF) {
                // Група дійшла до 254 ненульових байтів — закриваємо примусово.
                dst[code_i] = code;
                code = 1;
                code_i = write_i++;
                if (code_i >= dst.size()) {
                    return std::unexpected(Error::NoSpace);
                }
            }
        }
    }

    if (code_i >= dst.size()) {
        return std::unexpected(Error::NoSpace);
    }
    dst[code_i] = code;
    return write_i;
}

std::expected<std::size_t, Error> cobs_decode(Bytes src, std::span<std::uint8_t> dst) noexcept {
    if (src.empty()) {
        return std::unexpected(Error::CobsCorrupted);
    }

    std::size_t src_i = 0;
    std::size_t dst_i = 0;

    while (src_i < src.size()) {
        const std::uint8_t code = src[src_i++];
        if (code == 0x00) {
            return std::unexpected(Error::CobsCorrupted);   // нуль усередині тіла
        }

        for (std::uint8_t i = 1; i < code; ++i) {
            if (src_i >= src.size() || dst_i >= dst.size()) {
                return std::unexpected(Error::CobsCorrupted);
            }
            dst[dst_i++] = src[src_i++];
        }

        // Останню групу нуль не закриває: він і був роздільником кадру.
        if (code < 0xFF && src_i < src.size()) {
            if (dst_i >= dst.size()) {
                return std::unexpected(Error::CobsCorrupted);
            }
            dst[dst_i++] = 0x00;
        }
    }

    return dst_i;
}

}  // namespace link::codec
