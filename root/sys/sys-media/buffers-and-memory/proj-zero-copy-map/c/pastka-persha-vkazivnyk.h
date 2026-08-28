/* ✗ так не можна */
static const guint8 *g_last_y;
static gint          g_last_stride;

gst_video_frame_map (&frame, &ctx->info, buf, GST_MAP_READ);
g_last_y      = GST_VIDEO_FRAME_PLANE_DATA   (&frame, 0);
g_last_stride = GST_VIDEO_FRAME_PLANE_STRIDE (&frame, 0);
gst_video_frame_unmap (&frame);
gst_sample_unref (sample);
/* …десь у зовсім іншій функції */
analyse (g_last_y, g_last_stride);
