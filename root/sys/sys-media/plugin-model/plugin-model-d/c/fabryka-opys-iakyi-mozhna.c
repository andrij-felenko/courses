static GstStaticPadTemplate sink_template =
GST_STATIC_PAD_TEMPLATE ("sink", GST_PAD_SINK, GST_PAD_ALWAYS,
    GST_STATIC_CAPS ("video/x-h264, stream-format=(string)byte-stream"));

static void
gst_my_filter_class_init (GstMyFilterClass * klass)
{
  GstElementClass *ec = GST_ELEMENT_CLASS (klass);

  gst_element_class_set_static_metadata (ec,
      "Мій фільтр", "Filter/Effect/Video",
      "Робить із кадром щось корисне", "Ім'я <mail@example.org>");
  gst_element_class_add_static_pad_template (ec, &sink_template);
}
