/* gstdemoflip.c — кадр або проходить, або повертається на 90° */
#include <gst/gst.h>
#include <gst/base/gstbasetransform.h>
#include <gst/video/video.h>

GST_DEBUG_CATEGORY_STATIC (demoflip_debug);
#define GST_CAT_DEFAULT demoflip_debug

typedef enum {
  DEMO_FLIP_NONE = 0,   /* нічого не робимо */
  DEMO_FLIP_RIGHT,      /* завжди поворот на 90° за годинниковою */
  DEMO_FLIP_AUTO        /* повертаємо, лише якщо цього хочуть нижче */
} DemoFlipMode;

typedef struct {
  GstBaseTransform parent;

  DemoFlipMode mode;            /* властивість; читати під GST_OBJECT_LOCK */

  GstVideoInfo in_info, out_info;
  gboolean negotiated;
  gboolean rotate;              /* що робити з кадром — вирішує set_caps */
} GstDemoFlip;

typedef struct { GstBaseTransformClass parent_class; } GstDemoFlipClass;

#define GST_TYPE_DEMO_FLIP (gst_demo_flip_get_type ())
#define GST_DEMO_FLIP(o) \
    (G_TYPE_CHECK_INSTANCE_CAST ((o), GST_TYPE_DEMO_FLIP, GstDemoFlip))

G_DEFINE_TYPE (GstDemoFlip, gst_demo_flip, GST_TYPE_BASE_TRANSFORM)

/* Обидва пади обіцяють те саме: GRAY8 будь-якого розміру.
   GST_VIDEO_CAPS_MAKE розгортається у video/x-raw із діапазонами
   width, height і framerate — писати їх руками не треба. */
#define DEMO_FLIP_CAPS GST_VIDEO_CAPS_MAKE ("GRAY8")

static GstStaticPadTemplate sink_tmpl = GST_STATIC_PAD_TEMPLATE ("sink",
    GST_PAD_SINK, GST_PAD_ALWAYS, GST_STATIC_CAPS (DEMO_FLIP_CAPS));
static GstStaticPadTemplate src_tmpl = GST_STATIC_PAD_TEMPLATE ("src",
    GST_PAD_SRC, GST_PAD_ALWAYS, GST_STATIC_CAPS (DEMO_FLIP_CAPS));

enum { PROP_0, PROP_MODE };

/* Щоб `mode` показувався в gst-inspect словами, а не числами,
   перелік треба зареєструвати як тип. */
#define GST_TYPE_DEMO_FLIP_MODE (gst_demo_flip_mode_get_type ())
static GType
gst_demo_flip_mode_get_type (void)
{
  static const GEnumValue values[] = {
    {DEMO_FLIP_NONE,  "Не чіпати кадр",                 "none"},
    {DEMO_FLIP_RIGHT, "Завжди повертати на 90°",        "right"},
    {DEMO_FLIP_AUTO,  "Повертати, лише якщо просять",   "auto"},
    {0, NULL, NULL}
  };
  static gsize t = 0;

  if (g_once_init_enter (&t))
    g_once_init_leave (&t, g_enum_register_static ("DemoFlipMode", values));
  return (GType) t;
}

static void
gst_demo_flip_get_property (GObject * object, guint id,
    GValue * value, GParamSpec * pspec)
{
  GstDemoFlip *self = GST_DEMO_FLIP (object);

  if (id != PROP_MODE) {
    G_OBJECT_WARN_INVALID_PROPERTY_ID (object, id, pspec);
    return;
  }
  GST_OBJECT_LOCK (self);
  g_value_set_enum (value, self->mode);
  GST_OBJECT_UNLOCK (self);
}

static void
gst_demo_flip_set_property (GObject * object, guint id,
    const GValue * value, GParamSpec * pspec)
{
  GstDemoFlip *self = GST_DEMO_FLIP (object);

  if (id != PROP_MODE) {
    G_OBJECT_WARN_INVALID_PROPERTY_ID (object, id, pspec);
    return;
  }

  GST_OBJECT_LOCK (self);
  self->mode = g_value_get_enum (value);
  GST_OBJECT_UNLOCK (self);

  /* Множина, яку ми обіцяємо, щойно змінилась. Самі себе ми
     переузгодити не можемо — просимо базовий клас зробити це
     перед наступним кадром. */
  gst_base_transform_reconfigure_src (GST_BASE_TRANSFORM (self));
}
