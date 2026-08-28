/* trace-signals.c — усе, що проходить крізь пад, одним рядком на сигнал.
 *
 *   gcc trace-signals.c -o trace-signals $(pkg-config --cflags --libs gstreamer-1.0)
 */
#include <gst/gst.h>

typedef struct {
  const gchar *tag;        /* як звати цю точку спостереження */
  guint64      buffers;    /* скільки буферів уже пройшло крізь неї */
} Point;

static gint64      t_start;      /* монотонний час старту, мкс */
static GMutex      names_lock;
static GHashTable *names;        /* GThread* → «T1», «T2», … */
static guint       names_seq;

static gint64
ms_now (void)
{
  return (g_get_monotonic_time () - t_start) / 1000;
}

/* Коротке ім'я нитки: перша, що сюди зайшла, стає T1, друга — T2 і далі.
   Голий покажчик GThread* нічого не каже оку, а «T2» видно одразу. */
static const gchar *
thread_tag (void)
{
  GThread *self = g_thread_self ();
  gchar *name;

  g_mutex_lock (&names_lock);
  name = g_hash_table_lookup (names, self);
  if (name == NULL) {
    name = g_strdup_printf ("T%u", ++names_seq);
    g_hash_table_insert (names, self, name);
  }
  g_mutex_unlock (&names_lock);
  return name;
}
