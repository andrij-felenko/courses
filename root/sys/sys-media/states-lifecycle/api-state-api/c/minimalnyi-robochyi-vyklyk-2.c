GstElement *pipeline = gst_parse_launch (
    "filesrc location=movie.mkv ! decodebin ! autovideosink", NULL);

if (await_state (pipeline, GST_STATE_PAUSED)) {
  gint64 dur;
  /* тільки тепер тривалість справді відома */
  if (gst_element_query_duration (pipeline, GST_FORMAT_TIME, &dur))
    g_print ("тривалість: %" GST_TIME_FORMAT "\n", GST_TIME_ARGS (dur));

  await_state (pipeline, GST_STATE_PLAYING);   /* коштує майже нічого */
}

gst_element_set_state (pipeline, GST_STATE_NULL);   /* обов'язково перед unref */
gst_object_unref (pipeline);
