static void
gst_demo_flip_class_init (GstDemoFlipClass * klass)
{
  GObjectClass *gobject_class = G_OBJECT_CLASS (klass);
  GstElementClass *element_class = GST_ELEMENT_CLASS (klass);
  GstBaseTransformClass *trans_class = GST_BASE_TRANSFORM_CLASS (klass);

  gobject_class->set_property = gst_demo_flip_set_property;
  gobject_class->get_property = gst_demo_flip_get_property;
  g_object_class_install_property (gobject_class, PROP_MODE,
      g_param_spec_enum ("mode", "Режим", "Що робити з кадром",
          GST_TYPE_DEMO_FLIP_MODE, DEMO_FLIP_AUTO,
          G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS |
          GST_PARAM_MUTABLE_PLAYING));

  gst_element_class_add_static_pad_template (element_class, &sink_tmpl);
  gst_element_class_add_static_pad_template (element_class, &src_tmpl);
  gst_element_class_set_static_metadata (element_class, "Demo flip",
      "Filter/Effect/Video", "Пропускає кадр або повертає на 90°", "Курс");

  trans_class->transform_caps = gst_demo_flip_transform_caps;
  trans_class->fixate_caps    = gst_demo_flip_fixate_caps;
  trans_class->set_caps       = gst_demo_flip_set_caps;
  trans_class->get_unit_size  = gst_demo_flip_get_unit_size;
  trans_class->transform      = gst_demo_flip_transform;
}

static void
gst_demo_flip_init (GstDemoFlip * self)
{
  self->mode = DEMO_FLIP_AUTO;
  self->negotiated = FALSE;
}

static gboolean
plugin_init (GstPlugin * plugin)
{
  GST_DEBUG_CATEGORY_INIT (demoflip_debug, "demoflip", 0, "demoflip");
  return gst_element_register (plugin, "demoflip", GST_RANK_NONE,
      GST_TYPE_DEMO_FLIP);
}

GST_PLUGIN_DEFINE (GST_VERSION_MAJOR, GST_VERSION_MINOR,
    demoflip, "Кадр або проходить, або повертається на 90°",
    plugin_init, "1.0", "LGPL", "demoflip", "https://example.org/")
