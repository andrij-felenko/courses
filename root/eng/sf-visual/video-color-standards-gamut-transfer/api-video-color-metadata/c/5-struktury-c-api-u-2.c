/* c */
#include <libswscale/swscale.h>
#include <libavutil/frame.h>

/**
 * Налаштування конвертера swscale з урахуванням колірних метаданих кадру
 */
struct SwsContext* create_color_converter(const AVFrame *src_frame,
                                           int dst_w, int dst_h,
                                           enum AVPixelFormat dst_fmt)
{
    struct SwsContext *sws_ctx = sws_getContext(
        src_frame->width, src_frame->height, src_frame->format,
        dst_w, dst_h, dst_fmt,
        SWS_BILINEAR, NULL, NULL, NULL
    );

    if (!sws_ctx) return NULL;

    /* Встановлення коефіцієнтів джерела та призначення */
    int src_colorspace = (src_frame->colorspace == AVCOL_SPC_BT2020_NCL) ? SWS_CS_BT2020 : SWS_CS_ITU709;
    int dst_colorspace = SWS_CS_DEFAULT; /* sRGB / BT.709 */

    int src_range = (src_frame->color_range == AVCOL_RANGE_JPEG) ? 1 : 0;
    int dst_range = 1; /* Full range RGB для відображення на моніторі */

    const int *inv_table, *table;
    int src_full, dst_full;
    int brightness, contrast, saturation;

    /* Зчитати поточні коефіцієнти */
    sws_getColorspaceDetails(sws_ctx, (int**)&inv_table, &src_full,
                             (int**)&table, &dst_full,
                             &brightness, &contrast, &saturation);

    inv_table = sws_getCoefficients(src_colorspace);
    table = sws_getCoefficients(dst_colorspace);

    /* Перевизначити матриці та рівні квантування */
    sws_setColorspaceDetails(sws_ctx, inv_table, src_range,
                             table, dst_range,
                             brightness, contrast, saturation);

    return sws_ctx;
}
