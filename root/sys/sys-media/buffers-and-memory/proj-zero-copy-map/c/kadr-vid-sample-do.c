/* Іде рядками площини яскравості за СПРАВЖНІМ кроком і складає профіль. */
static void
build_profile (const GstVideoFrame *f, guint8 *out)
{
  const guint8 *y      = GST_VIDEO_FRAME_PLANE_DATA   (f, 0);
  gint          stride = GST_VIDEO_FRAME_PLANE_STRIDE (f, 0);
  gint          w      = GST_VIDEO_FRAME_WIDTH  (f);
  gint          h      = GST_VIDEO_FRAME_HEIGHT (f);

  guint64 acc[PROF_H] = { 0 };
  guint32 cnt[PROF_H] = { 0 };

  for (gint row = 0; row < h; row++) {
    const guint8 *line = y + (gsize) row * stride;      /* НЕ row * w */
    guint64 sum = 0;

    for (gint x = 0; x < w; x++)
      sum += line[x];

    gint bin = (gint) ((gint64) row * PROF_H / h);      /* h рядків → PROF_H смуг */
    acc[bin] += sum / (guint) w;
    cnt[bin] += 1;
  }

  memset (out, 0, PROF_BYTES);
  for (gint b = 0; b < PROF_H; b++) {
    guint mean = cnt[b] ? (guint) (acc[b] / cnt[b]) : 0;          /* 0…255 */
    gint  len  = (gint) ((guint64) mean * PROF_W / 255);
    memset (out + (gsize) b * PROF_STRIDE, 255, (gsize) len);
  }
}

static gboolean
process_one (GstAppSink *sink, Ctx *ctx)
{
  GstSample     *sample;
  GstBuffer     *buf, *out;
  GstCaps       *caps;
  GstVideoFrame  frame;
  gint           idx;
  gboolean       go_on = TRUE;

  sample = gst_app_sink_pull_sample (sink);          /* наш: transfer full */
  if (sample == NULL)
    return FALSE;                                    /* EOS або зупинка */

  buf  = gst_sample_get_buffer (sample);             /* позичений */
  caps = gst_sample_get_caps (sample);               /* позичений */
  if (buf == NULL || caps == NULL)
    goto out_sample;

  /* gst_caps_is_equal першою дією порівнює вказівники, а appsink зазвичай
     віддає той самий об'єкт caps — тож у сталому режимі це одне порівняння. */
  if (ctx->caps == NULL || !gst_caps_is_equal (caps, ctx->caps)) {
    if (!gst_video_info_from_caps (&ctx->info, caps))
      goto out_sample;
    gst_caps_replace (&ctx->caps, caps);             /* тепер тримаємо своє посилання */
    g_print ("формат: %s %d×%d\n",
             gst_video_format_to_string (GST_VIDEO_INFO_FORMAT (&ctx->info)),
             GST_VIDEO_INFO_WIDTH (&ctx->info),
             GST_VIDEO_INFO_HEIGHT (&ctx->info));
  }

  idx = slot_acquire (&g_ring);
  if (idx < 0) { go_on = FALSE; goto out_sample; }

  /* Тільки читання. Кожен зайвий біт у прапорцях тут коштує грошей. */
  if (!gst_video_frame_map (&frame, &ctx->info, buf, GST_MAP_READ))
    goto out_slot;

  build_profile (&frame, g_ring.data[idx]);

  gst_video_frame_unmap (&frame);                    /* далі frame.data — сміття */

  /* Слот переходить у власність буфера, буфер — у власність appsrc. */
  out = wrap_slot (idx, GST_BUFFER_PTS (buf), GST_BUFFER_DURATION (buf));
  if (gst_app_src_push_buffer (GST_APP_SRC (ctx->appsrc), out) != GST_FLOW_OK)
    go_on = FALSE;                                   /* слот уже у буфера — не чіпаємо */
  else
    ctx->frames++;

  goto out_sample;

out_slot:
  slot_release (&g_ring.ref[idx]);                   /* слот у конвеєр не пішов */
out_sample:
  gst_sample_unref (sample);
  return go_on;
}
