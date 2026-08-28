/* ncd_calculator.c — Обчислення NCD мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* Проста реалізація стиснення методом Run-Length Encoding (RLE)
   для демонстрації оцінки розміру C(x).
   У виробничих системах використовується zlib або liblzma. */
size_t compress_rle_size(const uint8_t *data, size_t len) {
    if (len == 0) return 0;
    size_t compressed_len = 0;
    size_t i = 0;
    
    while (i < len) {
        uint8_t run_byte = data[i];
        size_t run_len = 1;
        while (i + run_len < len && data[i + run_len] == run_byte && run_len < 255) {
            run_len++;
        }
        compressed_len += 2; /* 1 байт лічильника + 1 байт значення */
        i += run_len;
    }
    return compressed_len;
}

/* Обчислення NCD для двох бінарних буферів */
double compute_ncd_c(const uint8_t *x, size_t len_x,
                     const uint8_t *y, size_t len_y) {
    size_t cx = compress_rle_size(x, len_x);
    size_t cy = compress_rle_size(y, len_y);
    
    /* Конкатенація x та y */
    size_t len_xy = len_x + len_y;
    uint8_t *xy = (uint8_t *)malloc(len_xy);
    if (!xy) {
        return -1.0; /* Помилка виділення пам'яті */
    }
    memcpy(xy, x, len_x);
    memcpy(xy + len_x, y, len_y);
    
    size_t cxy = compress_rle_size(xy, len_xy);
    free(xy);
    
    size_t min_c = (cx < cy) ? cx : cy;
    size_t max_c = (cx > cy) ? cx : cy;
    
    if (max_c == 0) return 0.0;
    
    double ncd = (double)(cxy - min_c) / (double)max_c;
    return (ncd < 0.0) ? 0.0 : ((ncd > 1.0) ? 1.0 : ncd);
}

int main(void) {
    const char *text1 = "AAAAABBBBBCCCCCDDDDDAAAAABBBBBCCCCCDDDDD";
    const char *text2 = "AAAAABBBBBCCCCCDDDDDAAAAABBBBBCCCCCDDDDE";
    const char *text3 = "XYZ1234567890QWERTYSDFGHJKLZXCVBNMUIOP12";

    double ncd_12 = compute_ncd_c((const uint8_t *)text1, strlen(text1),
                                  (const uint8_t *)text2, strlen(text2));
    double ncd_13 = compute_ncd_c((const uint8_t *)text1, strlen(text1),
                                  (const uint8_t *)text3, strlen(text3));

    printf("NCD(text1, text2) = %.4f (близькі тексти)\n", ncd_12);
    printf("NCD(text1, text3) = %.4f (різні тексти)\n", ncd_13);

    return 0;
}
