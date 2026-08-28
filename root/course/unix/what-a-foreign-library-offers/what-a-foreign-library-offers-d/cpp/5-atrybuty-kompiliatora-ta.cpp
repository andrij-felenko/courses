#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <string_view>
#include <zstd.h>

struct ZstdContextDeleter {
    void operator()(ZSTD_CCtx* ctx) const noexcept {
        if (ctx) {
            ZSTD_freeCCtx(ctx);
        }
    }
};

using ScopedZstdCCtx = std::unique_ptr<ZSTD_CCtx, ZstdContextDeleter>;

std::expected<std::vector<uint8_t>, std::string_view> 
compress_payload(std::span<const uint8_t> input_data, int compression_level = 3) {
    // Безпечне керування контекстом через RAII
    ScopedZstdCCtx cctx(ZSTD_createCCtx());
    if (!cctx) {
        return std::unexpected("Не вдалося створити контекст ZSTD");
    }

    size_t const max_dst_size = ZSTD_compressBound(input_data.size());
    std::vector<uint8_t> output_buffer(max_dst_size);

    size_t const compressed_size = ZSTD_compressCCtx(
        cctx.get(),
        output_buffer.data(),
        output_buffer.size(),
        input_data.data(),
        input_data.size(),
        compression_level
    );

    if (ZSTD_isError(compressed_size)) {
        return std::unexpected(ZSTD_getErrorName(compressed_size));
    }

    output_buffer.resize(compressed_size);
    return output_buffer;
}
