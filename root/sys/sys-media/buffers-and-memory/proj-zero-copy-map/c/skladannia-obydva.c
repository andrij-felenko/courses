int
main (int argc, char *argv[])
{
  GstElement *in_pipe, *out_pipe, *sink, *src;
  GstCaps    *out_caps;
  Ctx         ctx = { 0 };

  gst_init (&argc, &argv);
  gst_video_info_init (&ctx.info);
  slot_ring_init (&g_ring);

  in_pipe = gst_parse_launch
      ("videotestsrc pattern=ball num-buffers=300 ! "
       "video/x-raw,format=NV12,width=1920,height=1080,framerate=30/1 ! "
       "appsink name=sink sync=false max-buffers=2 drop=true", NULL);

  out_pipe = gst_parse_launch
      ("appsrc name=src format=time is-live=true ! "
       "videoconvert ! videoscale ! autovideosink sync=false", NULL);

  sink = gst_bin_get_by_name (GST_BIN (in_pipe),  "sink");
  src  = gst_bin_get_by_name (GST_BIN (out_pipe), "src");
  ctx.appsrc = src;

  out_caps = gst_caps_new_simple ("video/x-raw",
      "format",    G_TYPE_STRING,     "GRAY8",
      "width",     G_TYPE_INT,        PROF_W,
      "height",    G_TYPE_INT,        PROF_H,
      "framerate", GST_TYPE_FRACTION, 30, 1, NULL);
  gst_app_src_set_caps (GST_APP_SRC (src), out_caps);
  gst_caps_unref (out_caps);

  gst_element_set_state (out_pipe, GST_STATE_PLAYING);
  gst_element_set_state (in_pipe,  GST_STATE_PLAYING);

  while (process_one (GST_APP_SINK (sink), &ctx))
    ;

  gst_app_src_end_of_stream (GST_APP_SRC (src));
  g_print ("оброблено кадрів: %" G_GUINT64_FORMAT "\n", ctx.frames);

  /* Спершу конвеєри в NULL — доки живий бодай один буфер, живий і слот. */
  gst_element_set_state (in_pipe,  GST_STATE_NULL);
  gst_element_set_state (out_pipe, GST_STATE_NULL);

  gst_object_unref (sink);
  gst_object_unref (src);
  gst_object_unref (in_pipe);
  gst_object_unref (out_pipe);
  gst_caps_replace (&ctx.caps, NULL);

  slot_ring_clear (&g_ring);        /* аж тепер жоден колбек уже не спрацює */
  return 0;
}
