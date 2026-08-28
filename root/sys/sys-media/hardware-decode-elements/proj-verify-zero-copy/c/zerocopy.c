/* zerocopy.c — чи справді кадр лишився в пристрої.
 *
 * gcc -O2 -Wall zerocopy.c -o zerocopy $(pkg-config --cflags --libs \
 *     gstreamer-1.0 gstreamer-app-1.0 gstreamer-video-1.0 gstreamer-allocators-1.0)
 */
#include <gst/gst.h>
#include <gst/app/gstappsink.h>
#include <gst/video/video.h>
#include <gst/allocators/gstdmabuf.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_HOLD 256

/* ---------- дрібна статистика ---------- */

typedef struct { gint64 *v; guint n, cap; } Series;

static void
series_add (Series * s, gint64 x)
{
  if (s->n == s->cap) {
    s->cap = s->cap ? s->cap * 2 : 256;
    s->v = g_renew (gint64, s->v, s->cap);
  }
  s->v[s->n++] = x;
}

static int
cmp_i64 (const void *a, const void *b)
{
  gint64 x = *(const gint64 *) a, y = *(const gint64 *) b;
  return (x > y) - (x < y);
}

/* Середнє тут не годиться: кілька витіснень планувальника тягнуть його вгору
   й ховають справжню ціну. Мінімум показує цю ціну без завад, медіана —
   типовий кадр, p95 — те, від чого захлинається показ. */
static gint64
series_report (Series * s, const char *what, guint skip)
{
  guint n;
  gint64 *v, med;

  if (s->n <= skip) {
    g_print ("%-24s замало вимірів\n", what);
    return 0;
  }
  n = s->n - skip;
  v = g_malloc (n * sizeof (gint64));
  memcpy (v, s->v + skip, n * sizeof (gint64));
  qsort (v, n, sizeof (gint64), cmp_i64);
  med = v[n / 2];
  g_print ("%-24s мін %8" G_GINT64_FORMAT "  медіана %8" G_GINT64_FORMAT
      "  p95 %8" G_GINT64_FORMAT "  макс %8" G_GINT64_FORMAT "  мкс\n",
      what, v[0], med, v[n * 95 / 100], v[n - 1]);
  g_free (v);
  return med;
}

/* ---------- який це шматок пам'яті ---------- */

/* «Тип» шматка живе не в самому GstMemory, а в його алокаторі, і то рядком.
   gst_memory_is_type() порівнює цей рядок з еталонним, не заглядаючи всередину;
   для друку беремо саме ім'я — так видно навіть типи, про які ми не знали. */
static const char *
memory_kind (GstMemory * mem, int *fd_out)
{
  *fd_out = -1;
  if (gst_is_dmabuf_memory (mem)) {
    *fd_out = gst_dmabuf_memory_get_fd (mem);
    return "DMABuf";
  }
  if (gst_memory_is_type (mem, GST_ALLOCATOR_SYSMEM))
    return "SystemMemory";
  /* VAMemory, CUDAMemory, GLMemory, NVMM… — усе, що плагін завів собі сам */
  return mem->allocator ? mem->allocator->mem_type : "(без алокатора)";
}

static void
dump_memories (GstBuffer * buf)
{
  guint i, n = gst_buffer_n_memory (buf);

  g_print ("буфер: %u шматок(ів), разом %" G_GSIZE_FORMAT " Б\n",
      n, gst_buffer_get_size (buf));
  for (i = 0; i < n; i++) {
    GstMemory *m = gst_buffer_peek_memory (buf, i);
    int fd;
    const char *kind = memory_kind (m, &fd);

    if (fd >= 0)
      g_print ("  [%u] %-14s %9" G_GSIZE_FORMAT " Б  fd=%d\n",
          i, kind, m->size, fd);
    else
      g_print ("  [%u] %-14s %9" G_GSIZE_FORMAT " Б\n", i, kind, m->size);
  }
}

/* ---------- дотик до пікселів ---------- */

static volatile guint64 keep_alive;    /* щоб оптимізатор не викинув цикл */

/* Один байт на кеш-лінію: сторінки таки під'єднуються, і з пам'яті реально
   приїжджає кожна лінія — тобто ми платимо за весь кадр, а не за 1/64 його. */
static gsize
touch_frame (GstVideoFrame * f)
{
  guint p;
  guint64 acc = 0;
  gsize bytes = 0;

  for (p = 0; p < GST_VIDEO_FRAME_N_PLANES (f); p++) {
    const guint8 *base = GST_VIDEO_FRAME_PLANE_DATA (f, p);
    gint stride = GST_VIDEO_FRAME_PLANE_STRIDE (f, p);
    gint h = GST_VIDEO_FRAME_COMP_HEIGHT (f, p);   /* NV12/I420: площина p ↔ компонента p */
    gint x, y;

    if (stride <= 0)                   /* перевернутий кадр — не наш випадок */
      continue;
    for (y = 0; y < h; y++) {
      const guint8 *row = base + (gsize) y * stride;

      for (x = 0; x < stride; x += 64)
        acc += row[x];
    }
    bytes += (gsize) h * stride;
  }
  keep_alive += acc;
  return bytes;
}

/* ---------- GstVideoInfo з caps, з поправкою на DMA_DRM ---------- */

static gboolean
video_info_from_caps (GstVideoInfo * info, GstCaps * caps)
{
  if (gst_video_info_from_caps (info, caps))
    return TRUE;
#if GST_CHECK_VERSION (1, 24, 0)
  {
    /* На caps із format=DMA_DRM звичайний розбір падає: колірний формат
       схований у полі drm-format разом із модифікатором розкладки. */
    GstVideoInfoDmaDrm drm;

    gst_video_info_dma_drm_init (&drm);
    if (gst_video_info_dma_drm_from_caps (&drm, caps)
        && gst_video_info_dma_drm_to_video_info (&drm, info))
      return TRUE;
  }
#endif
  return FALSE;
}

/* ---------- допоміжне ---------- */

static void
drain_errors (GstElement * pipeline)
{
  GstBus *bus = gst_element_get_bus (pipeline);
  GstMessage *msg;

  while ((msg = gst_bus_pop_filtered (bus, GST_MESSAGE_ERROR))) {
    GError *e = NULL;
    gchar *dbg = NULL;

    gst_message_parse_error (msg, &e, &dbg);
    g_printerr ("помилка від %s: %s\n", GST_OBJECT_NAME (msg->src), e->message);
    if (dbg)
      g_printerr ("  подробиці: %s\n", dbg);
    g_clear_error (&e);
    g_free (dbg);
    gst_message_unref (msg);
  }
  gst_object_unref (bus);
}

static gint64
cpu_time_us (void)
{
  struct timespec ts;

  if (clock_gettime (CLOCK_PROCESS_CPUTIME_ID, &ts) != 0)
    return 0;
  return (gint64) ts.tv_sec * 1000000 + ts.tv_nsec / 1000;
}

/* ---------- головне ---------- */

int
main (int argc, char **argv)
{
  const char *desc = NULL;
  gboolean do_map = FALSE, have_info = FALSE;
  guint want = 300, hold = 0, skip = 8, got = 0, i;
  GError *err = NULL;
  GstElement *pipeline, *probe;
  GstPad *pad;
  GstCaps *caps;
  GstCapsFeatures *feat;
  GstVideoInfo vinfo;
  GstSample *held[MAX_HOLD];
  Series t_map = { NULL, 0, 0 }, t_touch = { NULL, 0, 0 }, t_unmap = { NULL, 0, 0 };
  gsize frame_bytes = 0;
  gint64 wall0, wall1, cpu0, cpu1;
  gchar *str;

  gst_init (&argc, &argv);
  memset (held, 0, sizeof (held));

  for (i = 1; i < (guint) argc; i++) {
    if (!g_strcmp0 (argv[i], "--map"))
      do_map = TRUE;
    else if (!g_strcmp0 (argv[i], "--frames") && i + 1 < (guint) argc)
      want = atoi (argv[++i]);
    else if (!g_strcmp0 (argv[i], "--hold") && i + 1 < (guint) argc)
      hold = MIN (atoi (argv[++i]), MAX_HOLD);
    else if (!desc)
      desc = argv[i];
  }
  if (!desc) {
    g_printerr ("вжиток: %s \"<конвеєр з appsink name=probe>\""
        " [--map] [--frames N] [--hold N]\n", argv[0]);
    return 2;
  }

  pipeline = gst_parse_launch (desc, &err);
  if (!pipeline) {
    g_printerr ("конвеєр не зібрався: %s\n", err->message);
    return 1;
  }
  probe = gst_bin_get_by_name (GST_BIN (pipeline), "probe");
  if (!probe) {
    g_printerr ("у конвеєрі має бути appsink name=probe\n");
    return 1;
  }

  gst_element_set_state (pipeline, GST_STATE_PLAYING);
  /* Чекаємо не на команду, а на факт: доки перехід не завершився,
     узгоджених caps на паді ще немає, і питати нема про що. */
  if (gst_element_get_state (pipeline, NULL, NULL, 10 * GST_SECOND)
      != GST_STATE_CHANGE_SUCCESS) {
    drain_errors (pipeline);
    g_printerr ("конвеєр не дійшов до PLAYING\n");
    return 1;
  }

  pad = gst_element_get_static_pad (probe, "sink");
  caps = gst_pad_get_current_caps (pad);
  if (!caps) {
    g_printerr ("на паді немає узгоджених caps\n");
    return 1;
  }
  str = gst_caps_to_string (caps);
  g_print ("узгоджені caps : %s\n", str);
  g_free (str);

  feat = gst_caps_get_features (caps, 0);
  str = gst_caps_features_to_string (feat);
  g_print ("ознака пам'яті : %s\n", str);
  g_free (str);

  /* Порожній набір ознак рівносильний memory:SystemMemory — це той самий
     звичайний video/x-raw, тобто кадр уже в пам'яті процесу. */
  if (gst_caps_features_get_size (feat) == 0
      || gst_caps_features_contains (feat, GST_CAPS_FEATURE_MEMORY_SYSTEM_MEMORY))
    g_print ("вирок          : кадр у пам'яті процесу — копія вже сталася\n");
  else
    g_print ("вирок          : кадр лишився в чужій пам'яті\n");

  have_info = video_info_from_caps (&vinfo, caps);
  if (do_map && !have_info)
    g_printerr ("з цих caps GstVideoInfo не збирається — мапувати не будемо\n");

  wall0 = g_get_monotonic_time ();
  cpu0 = cpu_time_us ();

  while (got < want) {
    GstSample *smp =
        gst_app_sink_try_pull_sample (GST_APP_SINK (probe), 5 * GST_SECOND);
    GstBuffer *buf;

    if (!smp) {
      if (gst_app_sink_is_eos (GST_APP_SINK (probe)))
        g_print ("потік скінчився на %u-му кадрі\n", got);
      else
        g_print ("ЗАТИК: 5 с без кадру на %u-му (утримано зразків: %u)\n",
            got, MIN (got, hold));
      break;
    }
    buf = gst_sample_get_buffer (smp);

    if (got == 0)
      dump_memories (buf);

    if (do_map && have_info) {
      GstVideoFrame f;
      gint64 a = g_get_monotonic_time (), b, c, d;

      if (gst_video_frame_map (&f, &vinfo, buf, GST_MAP_READ)) {
        b = g_get_monotonic_time ();
        frame_bytes = touch_frame (&f);
        c = g_get_monotonic_time ();
        gst_video_frame_unmap (&f);
        d = g_get_monotonic_time ();
        series_add (&t_map, b - a);
        series_add (&t_touch, c - b);
        series_add (&t_unmap, d - c);
      } else if (got == 0) {
        g_printerr ("кадр не мапується на читання — пам'ять непрозора\n");
      }
    }

    if (hold) {
      guint slot = got % hold;

      if (held[slot])
        gst_sample_unref (held[slot]);
      held[slot] = smp;             /* зразок лишається нашим — і поверхня теж */
    } else {
      gst_sample_unref (smp);       /* поверхня повертається в пул саме тут */
    }
    got++;
  }

  wall1 = g_get_monotonic_time ();
  cpu1 = cpu_time_us ();

  g_print ("\nкадрів %u   час за годинником %.2f с (%.1f к/с)"
      "   процесорний час %.2f с (%.2f мс на кадр)\n",
      got, (wall1 - wall0) / 1e6,
      got ? got / ((wall1 - wall0) / 1e6) : 0.0,
      (cpu1 - cpu0) / 1e6, got ? (cpu1 - cpu0) / 1000.0 / got : 0.0);

  if (t_touch.n > skip) {
    gint64 med;

    series_report (&t_map, "gst_video_frame_map", skip);
    med = series_report (&t_touch, "читання кадру", skip);
    series_report (&t_unmap, "gst_video_frame_unmap", skip);
    if (med > 0)
      g_print ("%-24s %" G_GSIZE_FORMAT " Б за %" G_GINT64_FORMAT
          " мкс → %.0f МБ/с\n", "пропускна здатність",
          frame_bytes, med, frame_bytes / (double) med);
  }

  for (i = 0; i < MAX_HOLD; i++)
    if (held[i])
      gst_sample_unref (held[i]);
  gst_caps_unref (caps);
  gst_object_unref (pad);
  gst_object_unref (probe);
  gst_element_set_state (pipeline, GST_STATE_NULL);
  gst_object_unref (pipeline);
  g_free (t_map.v);
  g_free (t_touch.v);
  g_free (t_unmap.v);
  return 0;
}
