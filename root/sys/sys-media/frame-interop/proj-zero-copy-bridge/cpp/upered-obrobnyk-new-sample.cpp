static GstFlowReturn push_bgr (Bridge *b, const cv::Mat &bgr,
                               GstBuffer *src_buf, int w, int h);

static GstFlowReturn on_new_sample (GstAppSink *sink, gpointer user_data)
{
  Bridge *b = static_cast<Bridge *> (user_data);

  GstSample *sample = gst_app_sink_pull_sample (sink);   /* наш: transfer full */
  if (!sample)
    return GST_FLOW_EOS;

  /* Формат приїжджає з КОЖНИМ семплом; розбираємо його, лише коли він змінився. */
  GstCaps *caps = gst_sample_get_caps (sample);          /* позичений */
  if (!caps) { gst_sample_unref (sample); return GST_FLOW_ERROR; }

  if (!b->in_caps || !gst_caps_is_equal (caps, b->in_caps)) {
    if (!gst_video_info_from_caps (&b->in_info, caps) ||
        GST_VIDEO_INFO_FORMAT (&b->in_info) != GST_VIDEO_FORMAT_NV12) {
      g_printerr ("чекали NV12\n");
      gst_sample_unref (sample);
      return GST_FLOW_ERROR;
    }
    gst_caps_replace (&b->in_caps, caps);
    b->out_ready = false;                    /* вихід перенастроїмо під новий розмір */
  }

  GstBuffer *buf = gst_sample_get_buffer (sample);       /* позичений */

  /* Кроки й зсуви площин беруться з GstVideoMeta буфера, якщо вона там є,
     і лише інакше — з in_info. Порахувати їх із ширини не можна. */
  GstVideoFrame vf;
  if (!gst_video_frame_map (&vf, &b->in_info, buf, GST_MAP_READ)) {
    gst_sample_unref (sample);
    return GST_FLOW_ERROR;
  }

  const int w = GST_VIDEO_FRAME_WIDTH  (&vf);
  const int h = GST_VIDEO_FRAME_HEIGHT (&vf);

  /* Два заголовки на дві площини — кожен зі СВОЇМ покажчиком і СВОЇМ кроком. */
  cv::Mat y  (h,     w,     CV_8UC1,
              GST_VIDEO_FRAME_PLANE_DATA (&vf, 0),
              (size_t) GST_VIDEO_FRAME_PLANE_STRIDE (&vf, 0));
  cv::Mat uv (h / 2, w / 2, CV_8UC2,
              GST_VIDEO_FRAME_PLANE_DATA (&vf, 1),
              (size_t) GST_VIDEO_FRAME_PLANE_STRIDE (&vf, 1));

  /* Робота по яскравості йде просто по площині Y: нуль копій, нуль
     перетворень, повна роздільність. Декодер уже все зробив за нас. */
  std::vector<cv::Rect> hits;
  detect (y, hits);

  /* Колір потрібен лише тому, що кадр іде далі картинкою. bgr — ЛОКАЛЬНА
     змінна, і саме локальність тут рятує (див. пастку про create). */
  cv::Mat bgr;
  cv::cvtColorTwoPlane (y, uv, bgr, cv::COLOR_YUV2BGR_NV12);

  gst_video_frame_unmap (&vf);       /* з цієї миті y та uv — покажчики в нікуди */

  /* Малюємо вже у своїй пам'яті, а buf лишається дійсним: розмапування
     забирає покажчики на пікселі, а не саме посилання на буфер. */
  for (const cv::Rect &r : hits)
    cv::rectangle (bgr, r, cv::Scalar (0, 220, 0), 2);

  GstFlowReturn ret = push_bgr (b, bgr, buf, w, h);
  gst_sample_unref (sample);         /* аж тепер буфер повертається в пул */
  return ret;
}
