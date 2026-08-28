/* thread-map.c — друкує справжню мапу ниток конвеєра GStreamer.
 *
 * збірка:
 *   cc thread-map.c -o thread-map $(pkg-config --cflags --libs gstreamer-1.0)
 * запуск:
 *   ./thread-map              # із чергами на гілках — працює
 *   ./thread-map --no-queue   # без черг — конвеєр не доїде до PAUSED
 */
#include <gst/gst.h>

typedef struct {
  GThread *thread;   /* нитка, у якій спрацювала проба */
  gint     tid;      /* наш короткий номер: T1, T2, … */
  gchar   *elem;     /* ім'я елемента */
  gchar   *pad;      /* ім'я пада */
  gchar    dir;      /* '<' вхідний, '>' вихідний */
} Mark;

static GMutex      log_lock;   /* один замок на друк і на обидві таблиці */
static GArray     *marks;      /* Mark у порядку появи */
static GHashTable *tids;       /* GThread* → номер нитки */
static GThread    *thr[64];    /* номер нитки → GThread* */
static gint        next_tid = 1;

/* Короткий номер нитки. Викликати з узятим log_lock. */
static gint
thread_number (GThread *t)
{
  gpointer v = g_hash_table_lookup (tids, t);

  if (v == NULL && next_tid < (gint) G_N_ELEMENTS (thr)) {
    v = GINT_TO_POINTER (next_tid);
    thr[next_tid++] = t;
    g_hash_table_insert (tids, t, v);
  }
  return GPOINTER_TO_INT (v);
}
