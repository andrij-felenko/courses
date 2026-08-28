/* include/image.h — чистий публічний інтерфейс (C) */
#ifndef IMAGE_H
#define IMAGE_H

#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint32_t width;
    uint32_t height;
    uint8_t* pixels;
} ImageBuffer;

ImageBuffer* image_create(uint32_t w, uint32_t h);
void image_free(ImageBuffer* img);
int image_load_from_file(const char* path, ImageBuffer* out_img);

#endif
