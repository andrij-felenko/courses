typedef enum {
  GST_FORMAT_UNDEFINED = 0,
  GST_FORMAT_DEFAULT   = 1,   /* «природна» одиниця елемента: кадри, семпли */
  GST_FORMAT_BYTES     = 2,
  GST_FORMAT_TIME      = 3,   /* наносекунди — те, що вам потрібно в 95 % випадків */
  GST_FORMAT_BUFFERS   = 4,
  GST_FORMAT_PERCENT   = 5
} GstFormat;

#define GST_FORMAT_PERCENT_MAX    G_GINT64_CONSTANT (1000000)
#define GST_FORMAT_PERCENT_SCALE  G_GINT64_CONSTANT (10000)
