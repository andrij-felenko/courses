static void
gst_my_filter_class_init (GstMyFilterClass * klass)
{
  GstElementClass *element_class = GST_ELEMENT_CLASS (klass);
  GstBaseTransformClass *bt_class = GST_BASE_TRANSFORM_CLASS (klass);

  gst_element_class_set_static_metadata (element_class,
      "Інвертор яскравості",          /* людська назва */
      "Filter/Effect/Video",          /* klass: категорія для автопідбору */
      "Інвертує яскравість кадру GRAY8 на місці",
      "Ім'я Прізвище <mail@example.org>");

  gst_element_class_add_static_pad_template (element_class, &sink_template);
  gst_element_class_add_static_pad_template (element_class, &src_template);

  bt_class->set_caps = gst_my_filter_set_caps;
  bt_class->transform_ip = gst_my_filter_transform_ip;
}

static void
gst_my_filter_init (GstMyFilter * self)
{
  gst_video_info_init (&self->info);
}
