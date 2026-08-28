/* ── у класі елемента ─────────────────────────────────────────────────── */
enum { PROP_0, PROP_BITRATE };
enum { SIGNAL_KEYFRAME, SIGNAL_LAST };

static guint signals[SIGNAL_LAST];

static void gst_my_enc_set_property (GObject *, guint, const GValue *, GParamSpec *);
static void gst_my_enc_get_property (GObject *, guint,       GValue *, GParamSpec *);

static void
gst_my_enc_class_init (GstMyEncClass * klass)
{
  GObjectClass *go = G_OBJECT_CLASS (klass);

  go->set_property = gst_my_enc_set_property;
  go->get_property = gst_my_enc_get_property;

  g_object_class_install_property (go, PROP_BITRATE,
      g_param_spec_uint ("bitrate", "Bitrate", "Bitrate in kbit/sec",
          1, 2048000, 2048,
          G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS |
          G_PARAM_EXPLICIT_NOTIFY |          /* сповіщаємо самі, лише на зміну */
          GST_PARAM_MUTABLE_PLAYING | GST_PARAM_CONTROLLABLE));

  signals[SIGNAL_KEYFRAME] =
      g_signal_new ("keyframe", G_TYPE_FROM_CLASS (klass),
          G_SIGNAL_RUN_LAST, 0, NULL, NULL, NULL,
          G_TYPE_NONE, 1, G_TYPE_UINT64);   /* мітка часу опорного кадру */
}

static void
gst_my_enc_set_property (GObject * object, guint prop_id,
    const GValue * value, GParamSpec * pspec)
{
  GstMyEnc *self = GST_MY_ENC (object);

  switch (prop_id) {
    case PROP_BITRATE: {
      guint v = g_value_get_uint (value);
      gboolean changed;

      GST_OBJECT_LOCK (self);
      changed = (self->bitrate != v);
      self->bitrate = v;
      GST_OBJECT_UNLOCK (self);

      if (changed)                          /* EXPLICIT_NOTIFY: наш обов'язок */
        g_object_notify_by_pspec (object, pspec);
      break;
    }
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
  }
}

/* ── з боку застосунку ───────────────────────────────────────────────── */
GstElement *enc = gst_element_factory_make ("myenc", "enc");  /* floating */
gst_bin_add (GST_BIN (pipeline), enc);          /* ref_sink: власник — конвеєр */

g_object_set (enc, "bitrate", 4096, NULL);      /* значення копіюється всередину */

gulong id = g_signal_connect_data (enc, "notify::bitrate",
                                   G_CALLBACK (on_bitrate), ctx,
                                   (GClosureNotify) ctx_free, 0);

GstPad *sink = gst_element_get_static_pad (enc, "sink");   /* transfer full */
/* … робота … */
gst_object_unref (sink);                        /* пропущений unref = витік */

g_signal_handler_disconnect (enc, id);          /* ctx звільниться сам */
/* enc не чіпаємо: його власник — конвеєр */
