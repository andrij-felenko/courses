/* seek-driver.c — керування перемотуванням із застосунку.
 *
 * збірка:
 *   cc seek-driver.c -o seek-driver $(pkg-config --cflags --libs gstreamer-1.0)
 * режими:
 *   ./seek-driver goto    file:///шлях/clip.mp4 12.5
 *   ./seek-driver compare file:///шлях/clip.mp4 12.5
 *   ./seek-driver scrub   file:///шлях/clip.mp4
 *   ./seek-driver loop    file:///шлях/clip.mp4 10 20
 */
#include <gst/gst.h>

#define SEEK_TIMEOUT (10 * GST_SECOND)

typedef struct {
  GstElement *pipeline;
  GstBus     *bus;        /* окреме посилання: беремо раз, віддаємо раз */
  gboolean    seekable;
  gint64      lo, hi;     /* межі, у яких перемотування дозволене */
  gint64      duration;
} Player;

/* Чи можна тут перемотувати — і в яких межах. */
static gboolean
probe_seekable (Player *p)
{
  GstQuery *q = gst_query_new_seeking (GST_FORMAT_TIME);
  GstFormat fmt = GST_FORMAT_UNDEFINED;

  p->seekable = FALSE;
  p->lo = p->hi = 0;

  if (gst_element_query (p->pipeline, q)) {
    gst_query_parse_seeking (q, &fmt, &p->seekable, &p->lo, &p->hi);
    if (fmt != GST_FORMAT_TIME)      /* відповіли в іншій одиниці — для нас це «ні» */
      p->seekable = FALSE;
  } else {
    g_printerr ("  запит про перемотування лишився без відповіді\n");
  }
  gst_query_unref (q);

  if (!gst_element_query_duration (p->pipeline, GST_FORMAT_TIME, &p->duration))
    p->duration = GST_CLOCK_TIME_NONE;

  return p->seekable;
}
