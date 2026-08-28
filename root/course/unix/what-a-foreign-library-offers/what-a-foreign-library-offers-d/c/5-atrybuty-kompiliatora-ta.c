#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <zstd.h>

int compress_payload(const void* src, size_t src_size, void** out_buf, size_t* out_size) {
    /* Створення непрозорого контексту бібліотеки */
    ZSTD_CCtx* cctx = ZSTD_createCCtx();
    if (!cctx) {
        fprintf(stderr, "Помилка виділення контексту ZSTD\n");
        return -1;
    }

    /* Оцінка максимального розміру буфера стиснення */
    size_t const max_dst_size = ZSTD_compressBound(src_size);
    void* const dst = malloc(max_dst_size);
    if (!dst) {
        ZSTD_freeCCtx(cctx);
        return -1;
    }

    /* Виконання стиснення з рівнем 3 */
    size_t const compressed_size = ZSTD_compressCCtx(cctx, dst, max_dst_size, src, src_size, 3);
    
    /* Перевірка коду повернення на наявність помилки */
    if (ZSTD_isError(compressed_size)) {
        fprintf(stderr, "Помилка стиснення: %s\n", ZSTD_getErrorName(compressed_size));
        free(dst);
        ZSTD_freeCCtx(cctx);
        return -1;
    }

    /* Звільнення ресурсів бібліотеки */
    ZSTD_freeCCtx(cctx);

    *out_buf = dst;
    *out_size = compressed_size;
    return 0;
}
