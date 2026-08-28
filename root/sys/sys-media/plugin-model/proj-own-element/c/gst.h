/* gstmyfilter.c — інвертор яскравості GRAY8 на GstBaseTransform */
#include <gst/gst.h>
#include <gst/base/gstbasetransform.h>
#include <gst/video/video.h>

GST_DEBUG_CATEGORY_STATIC (myfilter_debug);
#define GST_CAT_DEFAULT myfilter_debug

#define GST_TYPE_MY_FILTER (gst_my_filter_get_type ())
G_DECLARE_FINAL_TYPE (GstMyFilter, gst_my_filter, GST, MY_FILTER,
    GstBaseTransform)

struct _GstMyFilter
{
  GstBaseTransform parent;
  GstVideoInfo info;            /* заповнює set_caps, читає transform_ip */
};

G_DEFINE_TYPE (GstMyFilter, gst_my_filter, GST_TYPE_BASE_TRANSFORM)

/* Єдиний формат, який елемент розуміє, — і той самий з обох боків:
   інверсія не міняє ані розкладки кадру, ані його розміру. */
#define MYFILTER_CAPS "video/x-raw, format=(string)GRAY8"

static GstStaticPadTemplate sink_template =
GST_STATIC_PAD_TEMPLATE ("sink", GST_PAD_SINK, GST_PAD_ALWAYS,
    GST_STATIC_CAPS (MYFILTER_CAPS));

static GstStaticPadTemplate src_template =
GST_STATIC_PAD_TEMPLATE ("src", GST_PAD_SRC, GST_PAD_ALWAYS,
    GST_STATIC_CAPS (MYFILTER_CAPS));
