int main (int argc, char *argv[])
{
  gst_init (&argc, &argv);
  std::signal (SIGINT, on_sigint);

  GError *err = NULL;
  GstElement *pin = gst_parse_launch (
      "videotestsrc pattern=smpte is-live=true ! "
      "video/x-raw,format=BGR,width=1280,height=720,framerate=30/1 ! "
      "appsink name=out sync=false max-buffers=2 drop=true", &err);
  if (!pin) { g_printerr ("вхід: %s\n", err->message); return 1; }

  GstElement *pout = gst_parse_launch (
      "appsrc name=in format=time is-live=true ! "
      "videoconvert ! autovideosink sync=false", &err);
  if (!pout) { g_printerr ("вихід: %s\n", err->message); return 1; }

  GstAppSink *sink = GST_APP_SINK (gst_bin_get_by_name (GST_BIN (pin),  "out"));
  GstAppSrc  *src  = GST_APP_SRC  (gst_bin_get_by_name (GST_BIN (pout), "in"));

  gst_element_set_state (pout, GST_STATE_PLAYING);
  gst_element_set_state (pin,  GST_STATE_PLAYING);

  GstVideoInfo  info;
  GstCaps      *known  = NULL;      /* caps, для яких порахована info */
  guint64       frames = 0;

  while (!g_stop) {
    GstSample *sample = gst_app_sink_try_pull_sample (sink, 200 * GST_MSECOND);
    if (!sample) {
      if (gst_app_sink_is_eos (sink)) break;
      continue;                                    /* таймаут — просто чекаємо */
    }

    GstCaps *caps = gst_sample_get_caps (sample);  /* позичені в sample */
    if (!caps) { gst_sample_unref (sample); continue; }

    /* Розбирати caps щокадру немає причини: між кадрами вони ті самі. */
    if (!known || !gst_caps_is_equal (caps, known)) {
      if (!gst_video_info_from_caps (&info, caps)) {
        gst_sample_unref (sample);
        break;
      }
      gst_caps_replace (&known, caps);             /* тепер посилання наше */
      gst_app_src_set_caps (src, known);           /* далі йде той самий формат */
      g_printerr ("формат %s %d×%d, крок площини 0 — з кадру, не з ширини\n",
                  gst_video_format_to_string (GST_VIDEO_INFO_FORMAT (&info)),
                  GST_VIDEO_INFO_WIDTH (&info), GST_VIDEO_INFO_HEIGHT (&info));
    }

    /* Буфер беремо СОБІ й одразу відпускаємо sample: доки той живий,
       у буфера два власники — і запис у нього коштував би копії. */
    GstBuffer *buf = gst_buffer_ref (gst_sample_get_buffer (sample));
    gst_sample_unref (sample);

    /* Власник один — повернеться той самий буфер. Якщо чомусь не один,
       GStreamer зробить нам власний, і програма лишиться правильною. */
    buf = gst_buffer_make_writable (buf);

    if (!blur_region (&info, buf, cv::Rect (420, 240, 440, 240))) {
      gst_buffer_unref (buf);                      /* не відобразився — наш борг */
      continue;
    }

    if (gst_app_src_push_buffer (src, buf) != GST_FLOW_OK)
      break;                                       /* після push buf уже не наш */
    ++frames;
  }

  /* Спершу зупиняємо той конвеєр, який тримає чужі буфери. */
  gst_app_src_end_of_stream (src);
  gst_element_set_state (pout, GST_STATE_NULL);
  gst_element_set_state (pin,  GST_STATE_NULL);

  if (known) gst_caps_unref (known);
  gst_object_unref (sink);
  gst_object_unref (src);
  gst_object_unref (pin);
  gst_object_unref (pout);

  g_printerr ("кадрів: %" G_GUINT64_FORMAT "\n", frames);
  return 0;
}
