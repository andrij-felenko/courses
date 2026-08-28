#include <stdint.h>
#include <stdio.h>

/* Оцінка стиснутого бітрейту (біт/с) з параметрів потоку. */
uint32_t estimate_bitrate(uint32_t w, uint32_t h, uint32_t fps,
                          float bits_per_pixel, float compression_ratio)
{
    /* сирий піксельний потік */
    double raw = (double)w * h * fps * bits_per_pixel;   /* біт/с */
    return (uint32_t)(raw / compression_ratio);
}

void choose_stream(void)
{
    /* HD, 30 к/с, YUV420 → 12 біт/піксель у середньому */
    uint32_t mjpeg = estimate_bitrate(1280, 720, 30, 12.0f, 10.0f);
    uint32_t h264  = estimate_bitrate(1280, 720, 30, 12.0f, 100.0f);

    printf("MJPEG: %u kbit/s\n", mjpeg / 1000);   /* ~33176 */
    printf("H.264: %u kbit/s\n", h264  / 1000);   /* ~3317  */

    /* радіоканал тримає, скажімо, 6 Мбіт/с надійно */
    const uint32_t link_capacity = 6000000;
    if (mjpeg > link_capacity)
        printf("MJPEG не влазить у канал — беремо H.264\n");
}
