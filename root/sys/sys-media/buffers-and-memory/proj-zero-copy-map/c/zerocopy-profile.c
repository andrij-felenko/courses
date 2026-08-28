/* zerocopy-profile.c — кадр із appsink без копії й результат назад у appsrc.
 *
 *   gcc -O2 -o zerocopy-profile zerocopy-profile.c \
 *       $(pkg-config --cflags --libs gstreamer-1.0 gstreamer-app-1.0 gstreamer-video-1.0)
 */
#include <gst/gst.h>
#include <gst/app/gstappsink.h>
#include <gst/app/gstappsrc.h>
#include <gst/video/video.h>
#include <string.h>

#define PROF_W       200                        /* видима ширина смужки      */
#define PROF_H       256                        /* рядків у профілі          */
#define PROF_STRIDE  256                        /* крок, вирівняний на 64    */
#define PROF_BYTES   ((gsize) PROF_STRIDE * PROF_H)
#define SLOT_COUNT   4

typedef struct _SlotRing SlotRing;

/* Те, що піде в колбек звільнення: кільце і номер слота в ньому.
   Кожен слот має свій незмінний SlotRef, тож на кадр не виділяється нічого. */
typedef struct {
  SlotRing *ring;
  gint      idx;
} SlotRef;

struct _SlotRing {
  guint8   *data[SLOT_COUNT];
  gboolean  busy[SLOT_COUNT];
  SlotRef   ref[SLOT_COUNT];
  GMutex    lock;
  GCond     freed;
};

/* Кільце мусить пережити обидва конвеєри: колбек звільнення спрацює
   на останньому unref буфера, а це буває вже під час зупинки. */
static SlotRing g_ring;

static void
slot_ring_init (SlotRing *r)
{
  g_mutex_init (&r->lock);
  g_cond_init (&r->freed);
  for (gint i = 0; i < SLOT_COUNT; i++) {
    r->data[i]     = g_malloc0 (PROF_BYTES);
    r->busy[i]     = FALSE;
    r->ref[i].ring = r;
    r->ref[i].idx  = i;
  }
}

static void
slot_ring_clear (SlotRing *r)
{
  for (gint i = 0; i < SLOT_COUNT; i++) {
    g_assert (!r->busy[i]);                     /* усі повернулися з конвеєра */
    g_free (r->data[i]);
  }
  g_mutex_clear (&r->lock);
  g_cond_clear (&r->freed);
}

static gint
slot_acquire (SlotRing *r)
{
  gint idx = -1;

  g_mutex_lock (&r->lock);
  while (idx < 0) {
    for (gint i = 0; i < SLOT_COUNT; i++)
      if (!r->busy[i]) { r->busy[i] = TRUE; idx = i; break; }

    if (idx < 0) {                              /* усі слоти в конвеєрі */
      gint64 deadline = g_get_monotonic_time () + 2 * G_TIME_SPAN_SECOND;
      if (!g_cond_wait_until (&r->freed, &r->lock, deadline))
        break;                                  /* дві секунди тиші — здаємось */
    }
  }
  g_mutex_unlock (&r->lock);
  return idx;
}

/* Це і є GDestroyNotify: GStreamer покличе його на останньому unref буфера,
   з невідомого нам потоку і в невідомий момент. */
static void
slot_release (gpointer user_data)
{
  SlotRef *sr = user_data;

  g_mutex_lock (&sr->ring->lock);
  sr->ring->busy[sr->idx] = FALSE;
  g_cond_signal (&sr->ring->freed);
  g_mutex_unlock (&sr->ring->lock);
}

typedef struct {
  GstVideoInfo  info;
  GstCaps      *caps;                           /* caps, для яких порахована info */
  GstElement   *appsrc;
  guint64       frames;
} Ctx;
