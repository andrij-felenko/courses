static GstBuffer *
wrap_slot (gint idx, GstClockTime pts, GstClockTime dur)
{
  gsize offset[1] = { 0 };
  gint  stride[1] = { PROF_STRIDE };
  GstBuffer *out;

  /* READONLY: нижчі елементи хай не пишуть у наш слот — ми його перевикористаємо.
     Останній unref покличе slot_release із &g_ring.ref[idx]. */
  out = gst_buffer_new_wrapped_full (GST_MEMORY_FLAG_READONLY,
                                     g_ring.data[idx],   /* дані     */
                                     PROF_BYTES,         /* maxsize  */
                                     0,                  /* offset   */
                                     PROF_BYTES,         /* size     */
                                     &g_ring.ref[idx],   /* user_data */
                                     slot_release);      /* GDestroyNotify */

  /* Крок 256 при ширині 200: без метаданих кожен нижчий елемент рахував би
     розкладку за шириною (для GRAY8 це 200) і отримав би скіс. */
  gst_buffer_add_video_meta_full (out, GST_VIDEO_FRAME_FLAG_NONE,
                                  GST_VIDEO_FORMAT_GRAY8,
                                  PROF_W, PROF_H, 1, offset, stride);

  GST_BUFFER_PTS (out)      = pts;                /* мітки беремо з вхідного кадру */
  GST_BUFFER_DURATION (out) = dur;
  return out;
}
