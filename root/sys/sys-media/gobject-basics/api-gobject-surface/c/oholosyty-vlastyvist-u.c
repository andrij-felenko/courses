enum { PROP_0, PROP_BITRATE, PROP_LOCATION, PROP_LAST };

static void
gst_my_enc_class_init (GstMyEncClass * klass)
{
  GObjectClass *gobject_class = G_OBJECT_CLASS (klass);

  gobject_class->set_property = gst_my_enc_set_property;
  gobject_class->get_property = gst_my_enc_get_property;

  g_object_class_install_property (gobject_class, PROP_BITRATE,
      g_param_spec_uint ("bitrate", "Bitrate", "Bitrate in kbit/sec",
          1, 2048000, 2048,
          G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS | GST_PARAM_MUTABLE_PLAYING));
}
