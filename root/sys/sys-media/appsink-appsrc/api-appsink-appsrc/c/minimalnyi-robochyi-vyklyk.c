typedef struct { guint64 n; } Ctx;

static void need_data (GstAppSrc *src, guint length, gpointer user_data)
{
  Ctx *ctx = user_data;

  if (ctx->n >= 300) {                         /* дані скінчилися */
    gst_app_src_end_of_stream (src);           /* без цього mp4mux не допише moov */
    return;
  }

  GstBuffer *buf = gst_buffer_new_allocate (NULL, 1920 * 1080 * 3, NULL);
  fill_frame (buf, ctx->n);                    /* ваш код малює кадр */

  GST_BUFFER_PTS (buf)      = ctx->n * GST_SECOND / 30;
  GST_BUFFER_DURATION (buf) = GST_SECOND / 30;
  ctx->n++;

  GstFlowReturn ret = gst_app_src_push_buffer (src, buf);   /* transfer full */
  if (ret != GST_FLOW_OK)
    gst_app_src_end_of_stream (src);           /* FLUSHING або EOS — далі не штовхаємо */
}

/* налаштування елемента */
GstAppSrc *src = GST_APP_SRC (gst_element_factory_make ("appsrc", "in"));

GstCaps *caps = gst_caps_new_simple ("video/x-raw",
    "format",    G_TYPE_STRING, "BGR",
    "width",     G_TYPE_INT,    1920,
    "height",    G_TYPE_INT,    1080,
    "framerate", GST_TYPE_FRACTION, 30, 1, NULL);
gst_app_src_set_caps (src, caps);
gst_caps_unref (caps);                         /* set_caps узяв своє посилання */

g_object_set (src, "format", GST_FORMAT_TIME,  /* НЕ bytes */
                   "is-live", TRUE,
                   "max-buffers", (guint64) 4, /* 4 × 6.2 МБ, а не 200 кБ */
                   NULL);

GstAppSrcCallbacks cb = { 0 };                 /* обнулити ОБОВ'ЯЗКОВО */
cb.need_data = need_data;
gst_app_src_set_callbacks (src, &cb, ctx, NULL);
