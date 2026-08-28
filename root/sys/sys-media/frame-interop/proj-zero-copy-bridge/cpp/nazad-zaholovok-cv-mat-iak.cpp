/* GStreamer покличе це, коли зникне ОСТАННЄ посилання на буфер, —
   з невідомого нам потоку й у невідому мить. Робота тут одна: −1 до лічильника. */
static void release_keeper (gpointer p)
{
  delete static_cast<cv::Mat *> (p);
}

static GstFlowReturn push_bgr (Bridge *b, const cv::Mat &bgr,
                               GstBuffer *src_buf, int w, int h)
{
  CV_Assert (bgr.isContinuous ());     /* wrapped_full знає довжину, а не крок */

  const gsize bytes  = bgr.total () * bgr.elemSize ();
  cv::Mat    *keeper = new cv::Mat (bgr);   /* копія ЗАГОЛОВКА: +1 до лічильника блока */

  GstBuffer *out = gst_buffer_new_wrapped_full (
      GST_MEMORY_FLAG_READONLY,      /* блок наш — нижчі елементи в нього не пишуть */
      keeper->data, bytes,           /* дані, maxsize */
      0, bytes,                      /* offset, size  */
      keeper, release_keeper);       /* хто відпустить останнім, той і поверне блок */

  /* Ширина не кратна чотирьом: сусідній елемент порахував би крок сам
     і промахнувся. Кажемо справжній крок метаданими. */
  gsize offset[GST_VIDEO_MAX_PLANES] = { 0 };
  gint  stride[GST_VIDEO_MAX_PLANES] = { (gint) bgr.step[0] };
  gst_buffer_add_video_meta_full (out, GST_VIDEO_FRAME_FLAG_NONE,
                                  GST_VIDEO_FORMAT_BGR, w, h, 1, offset, stride);

  /* Час беремо з вхідного кадру. Саме час — і НЕ метадані: там розкладка NV12. */
  gst_buffer_copy_into (out, src_buf,
                        (GstBufferCopyFlags) (GST_BUFFER_COPY_TIMESTAMPS |
                                              GST_BUFFER_COPY_FLAGS),
                        0, (gsize) -1);

  if (!b->out_ready) {
    GstCaps *ocaps = gst_caps_new_simple (
        "video/x-raw",
        "format",    G_TYPE_STRING,     "BGR",
        "width",     G_TYPE_INT,        w,
        "height",    G_TYPE_INT,        h,
        "framerate", GST_TYPE_FRACTION, GST_VIDEO_INFO_FPS_N (&b->in_info),
                                        GST_VIDEO_INFO_FPS_D (&b->in_info),
        NULL);
    gst_app_src_set_caps (GST_APP_SRC (b->src), ocaps);
    gst_caps_unref (ocaps);
    b->out_ready = true;
  }

  return gst_app_src_push_buffer (GST_APP_SRC (b->src), out);   /* забирає володіння */
}
