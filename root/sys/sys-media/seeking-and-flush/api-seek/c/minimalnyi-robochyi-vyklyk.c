#include <gst/gst.h>

static gboolean
seek_and_wait (GstElement *pipeline, gint64 pos_ns, gboolean accurate)
{
  GstQuery *q = gst_query_new_seeking (GST_FORMAT_TIME);
  gboolean seekable = FALSE;
  gint64 lo = 0, hi = 0;

  /* 1. чи взагалі можна і в яких межах */
  if (!gst_element_query (pipeline, q)) {
    gst_query_unref (q);
    return FALSE;                       /* ніхто не відповів — не перемотуємо */
  }
  gst_query_parse_seeking (q, NULL, &seekable, &lo, &hi);
  gst_query_unref (q);

  if (!seekable || pos_ns < lo || (hi != -1 && pos_ns > hi))
    return FALSE;

  /* 2. прохання; FLUSH обов'язковий, якщо файл уже дограв до кінця */
  GstSeekFlags flags = GST_SEEK_FLAG_FLUSH |
      (accurate ? GST_SEEK_FLAG_ACCURATE : GST_SEEK_FLAG_KEY_UNIT);

  if (!gst_element_seek (pipeline, 1.0, GST_FORMAT_TIME, flags,
          GST_SEEK_TYPE_SET, pos_ns,
          GST_SEEK_TYPE_SET, GST_CLOCK_TIME_NONE))
    return FALSE;                       /* ніхто не взявся */

  /* 3. справжнє завершення — ASYNC_DONE від самого конвеєра */
  GstBus *bus = gst_element_get_bus (pipeline);
  GstMessage *msg = gst_bus_timed_pop_filtered (bus, 5 * GST_SECOND,
      GST_MESSAGE_ASYNC_DONE | GST_MESSAGE_ERROR);
  gboolean ok = (msg && GST_MESSAGE_TYPE (msg) == GST_MESSAGE_ASYNC_DONE);

  if (msg)
    gst_message_unref (msg);
  gst_object_unref (bus);
  return ok;
}
