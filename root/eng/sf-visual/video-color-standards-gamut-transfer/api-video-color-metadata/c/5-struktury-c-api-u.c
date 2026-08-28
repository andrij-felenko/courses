#include <libavutil/frame.h>
#include <libavutil/pixfmt.h>

/* Структура кадру у C API FFmpeg */
typedef struct AVFrame {
    uint8_t *data[AV_NUM_DATA_POINTERS];
    int linesize[AV_NUM_DATA_POINTERS];
    
    int width, height;
    enum AVPixelFormat format; /* наприклад, AV_PIX_FMT_YUV420P */

    /* Метадані колірного простору кадру */
    enum AVColorRange color_range;            /* AVCOL_RANGE_MPEG (Limited) чи AVCOL_RANGE_JPEG (Full) */
    enum AVColorPrimaries color_primaries;    /* AVCOL_PRI_BT709, AVCOL_PRI_BT2020 тощо */
    enum AVColorTransferCharacteristic color_trc; /* AVCOL_TRC_BT709, AVCOL_TRC_SMPTE2084 тощо */
    enum AVColorSpace colorspace;             /* AVCOL_SPC_BT709, AVCOL_SPC_BT2020_NCL тощо */
    
    enum AVChromaLocation chroma_location;   /* AVCHROMA_LOC_LEFT, AVCHROMA_LOC_CENTER */
} AVFrame;
