GstElement *sink = gst_bin_get_by_name (GST_BIN (pipeline), "out");
g_object_set (sink, "sync", FALSE, "max-buffers", (guint) 2, NULL);

for (;;) {
  GstSample *sample =
      gst_app_sink_try_pull_sample (GST_APP_SINK (sink), GST_SECOND);
  if (!sample) {                       /* таймаут або кінець потоку */
    if (gst_app_sink_is_eos (GST_APP_SINK (sink)))
      break;
    continue;
  }

  GstBuffer *buf = gst_sample_get_buffer (sample);  /* належить семплу */
  GstMapInfo info;
  if (gst_buffer_map (buf, &info, GST_MAP_READ)) {
    process (info.data, info.size);
    gst_buffer_unmap (buf, &info);
  }
  gst_sample_unref (sample);           /* пам'ять повертається в пул */
}
