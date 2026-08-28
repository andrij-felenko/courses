/* latency-probe.c — вік буфера в кількох точках живого конвеєра GStreamer.
 *
 *   gcc -O2 latency-probe.c -o latency-probe \
 *       $(pkg-config --cflags --libs gstreamer-1.0)
 *
 *   ./latency-probe "<опис конвеєра>" елемент:пад [елемент:пад ...]
 */
#include <gst/gst.h>

#define HIST_MS 2048                 /* гістограма до 2.048 с із кроком 1 мс */
#define WARMUP  (2 * GST_SECOND)     /* перші дві секунди не рахуємо */

typedef struct _Probe Probe;

typedef struct {
  Probe        *owner;
  gchar        *label;
  GstSegment    segment;             /* чіпає лише потік цього пада */
  gboolean      have_segment;
  guint64       n, late;             /* нижче — під замком */
  GstClockTime  worst;
  guint32       hist[HIST_MS];
} Point;

struct _Probe {
  GstElement   *pipeline;
  GMainLoop    *loop;
  GMutex        lock;
  Point         pt[16];
  guint         n_points;
  gboolean      live;
  GstClockTime  contract, ceiling;
};

/* ── 1. Що конвеєр ПООБІЦЯВ ───────────────────────────────────────────── */
static void
read_contract (Probe *pr)
{
  GstQuery *q = gst_query_new_latency ();
  gboolean live = FALSE;
  GstClockTime min = GST_CLOCK_TIME_NONE, max = GST_CLOCK_TIME_NONE;

  if (gst_element_query (pr->pipeline, q))
    gst_query_parse_latency (q, &live, &min, &max);
  gst_query_unref (q);

  g_mutex_lock (&pr->lock);
  pr->live = live;
  pr->contract = min;         /* саме це число споживач додає до дедлайну */
  pr->ceiling = max;          /* GST_CLOCK_TIME_NONE = стелі немає */
  g_mutex_unlock (&pr->lock);
}

/* ── 2. Що вийшло НАСПРАВДІ ───────────────────────────────────────────── */
static GstPadProbeReturn
on_pad (GstPad *pad, GstPadProbeInfo *info, gpointer user_data)
{
  Point *p = user_data;
  Probe *pr = p->owner;
  GstBuffer *buf;
  GstClock *clock;
  GstClockTime pts, rt_buf, base, abs_now, now, age;

  /* Сегмент серіалізований з буферами й іде тим самим потоком,
     тож зберігаємо його просто тут — замок не потрібен. */
  if (GST_PAD_PROBE_INFO_TYPE (info) & GST_PAD_PROBE_TYPE_EVENT_DOWNSTREAM) {
    GstEvent *ev = GST_PAD_PROBE_INFO_EVENT (info);
    if (GST_EVENT_TYPE (ev) == GST_EVENT_SEGMENT) {
      gst_event_copy_segment (ev, &p->segment);
      p->have_segment = TRUE;
    }
    return GST_PAD_PROBE_OK;
  }

  buf = GST_PAD_PROBE_INFO_BUFFER (info);
  pts = GST_BUFFER_PTS (buf);
  if (!p->have_segment || !GST_CLOCK_TIME_IS_VALID (pts))
    return GST_PAD_PROBE_OK;

  /* позиція буфера у спільній шкалі конвеєра */
  rt_buf = gst_segment_to_running_time (&p->segment, GST_FORMAT_TIME, pts);
  if (!GST_CLOCK_TIME_IS_VALID (rt_buf))        /* мітка поза сегментом */
    return GST_PAD_PROBE_OK;

  /* «зараз» у ТІЙ САМІЙ шкалі: показ годинника мінус базовий час.
     Дослівно те, що з 1.18 робить gst_element_get_current_running_time(). */
  clock = gst_element_get_clock (pr->pipeline);
  if (clock == NULL)                            /* годинника ще не обрано */
    return GST_PAD_PROBE_OK;
  base = gst_element_get_base_time (pr->pipeline);
  abs_now = gst_clock_get_time (clock);
  gst_object_unref (clock);

  if (!GST_CLOCK_TIME_IS_VALID (base) ||
      !GST_CLOCK_TIME_IS_VALID (abs_now) || abs_now < base)
    return GST_PAD_PROBE_OK;                    /* base_time ще не зафіксовано */
  now = abs_now - base;

  /* now < rt_buf — дані попереду годинника, тобто джерело не живе;
     now < WARMUP — розігрів, ці виміри брехливі (див. далі). */
  if (now < rt_buf || now < WARMUP)
    return GST_PAD_PROBE_OK;

  age = now - rt_buf;

  /* У потоковому потоці — тільки арифметика. Жодного вводу-виводу. */
  g_mutex_lock (&pr->lock);
  {
    guint ms = (guint) (age / GST_MSECOND);
    p->hist[ms < HIST_MS ? ms : HIST_MS - 1]++;
    p->n++;
    if (age > p->worst)
      p->worst = age;
    if (GST_CLOCK_TIME_IS_VALID (pr->contract) && age > pr->contract)
      p->late++;
  }
  g_mutex_unlock (&pr->lock);

  return GST_PAD_PROBE_OK;
}

/* ── 3. Звіт: квантилі з гістограми й приріст між точками ─────────────── */
static double
quantile_ms (const Point *p, double q)
{
  guint64 need = (guint64) (p->n * q), acc = 0;
  guint i;

  for (i = 0; i < HIST_MS; i++) {
    acc += p->hist[i];
    if (acc > 0 && acc >= need)
      return i;
  }
  return -1.0;
}

static const gchar *                            /* один виклик на g_print! */
ms_str (GstClockTime t)
{
  static gchar buf[32];
  if (!GST_CLOCK_TIME_IS_VALID (t))
    return "∞";
  g_snprintf (buf, sizeof buf, "%.1f мс", t / (double) GST_MSECOND);
  return buf;
}

static gboolean
report (gpointer user_data)
{
  Probe *pr = user_data;
  double prev = 0;
  guint i;

  read_contract (pr);                  /* число могло змінитися на ходу */

  g_mutex_lock (&pr->lock);
  g_print ("\nконтракт: live=%s  min=%s", pr->live ? "так" : "ні",
           ms_str (pr->contract));
  g_print ("  max=%s\n", ms_str (pr->ceiling));
  g_print ("%-24s %7s %8s %8s %8s %9s\n",
           "точка", "n", "p50", "p95", "макс", "приріст");

  for (i = 0; i < pr->n_points; i++) {
    Point *p = &pr->pt[i];
    double p50, p95;

    if (p->n == 0) {
      g_print ("%-24s       —\n", p->label);
      continue;
    }
    p50 = quantile_ms (p, 0.50);
    p95 = quantile_ms (p, 0.95);
    g_print ("%-24s %7" G_GUINT64_FORMAT " %8.0f %8.0f %8.1f %+9.0f\n",
             p->label, p->n, p50, p95,
             p->worst / (double) GST_MSECOND, p50 - prev);
    prev = p50;

    if (i + 1 == pr->n_points && GST_CLOCK_TIME_IS_VALID (pr->contract)) {
      double budget = pr->contract / (double) GST_MSECOND;
      g_print ("   запас до дедлайну: p50 %+.0f мс, p95 %+.0f мс; "
               "після дедлайну %" G_GUINT64_FORMAT " з %" G_GUINT64_FORMAT
               " (%.1f%%)\n",
               budget - p50, budget - p95, p->late, p->n,
               100.0 * p->late / p->n);
    }
  }
  g_mutex_unlock (&pr->lock);
  return G_SOURCE_CONTINUE;
}

/* ── 4. Шина: без цього контракт застаріває ───────────────────────────── */
static gboolean
on_bus (GstBus *bus, GstMessage *msg, gpointer user_data)
{
  Probe *pr = user_data;

  switch (GST_MESSAGE_TYPE (msg)) {
    case GST_MESSAGE_LATENCY:
      /* Хтось змінив свій внесок: rtspsrc додав пад, буфер джитера
         переоцінив мережу. Перерахувати й розіслати наново. */
      gst_bin_recalculate_latency (GST_BIN (pr->pipeline));
      read_contract (pr);
      g_print ("↻ затримку перераховано: %s\n", ms_str (pr->contract));
      break;

    case GST_MESSAGE_STATE_CHANGED:
      if (GST_MESSAGE_SRC (msg) == GST_OBJECT (pr->pipeline)) {
        GstState now;
        gst_message_parse_state_changed (msg, NULL, &now, NULL);
        if (now == GST_STATE_PLAYING)
          read_contract (pr);          /* аж тепер є годинник і base_time */
      }
      break;

    case GST_MESSAGE_ERROR: {
      GError *err = NULL;
      gchar *dbg = NULL;
      gst_message_parse_error (msg, &err, &dbg);
      g_printerr ("помилка: %s\n%s\n", err->message, dbg ? dbg : "");
      g_clear_error (&err);
      g_free (dbg);
      g_main_loop_quit (pr->loop);
      break;
    }

    case GST_MESSAGE_EOS:
      g_main_loop_quit (pr->loop);
      break;

    default:
      break;
  }
  return TRUE;
}

/* ── 5. Складання ─────────────────────────────────────────────────────── */
static gboolean
add_point (Probe *pr, const gchar *spec)         /* «dec:src» */
{
  gchar **bits = g_strsplit (spec, ":", 2);
  GstElement *el;
  GstPad *pad;
  Point *p;

  if (bits[0] == NULL || bits[1] == NULL) {
    g_printerr ("точка має вигляд «елемент:пад», а не «%s»\n", spec);
    g_strfreev (bits);
    return FALSE;
  }
  el = gst_bin_get_by_name (GST_BIN (pr->pipeline), bits[0]);
  if (el == NULL) {
    g_printerr ("немає елемента «%s» — дайте йому name= в описі конвеєра\n",
                bits[0]);
    g_strfreev (bits);
    return FALSE;
  }
  pad = gst_element_get_static_pad (el, bits[1]);
  gst_object_unref (el);
  if (pad == NULL) {
    g_printerr ("в елемента «%s» немає статичного пада «%s»\n",
                bits[0], bits[1]);
    g_strfreev (bits);
    return FALSE;
  }
  g_strfreev (bits);

  p = &pr->pt[pr->n_points++];
  p->owner = pr;
  p->label = g_strdup (spec);
  gst_segment_init (&p->segment, GST_FORMAT_UNDEFINED);

  gst_pad_add_probe (pad,
      GST_PAD_PROBE_TYPE_BUFFER | GST_PAD_PROBE_TYPE_EVENT_DOWNSTREAM,
      on_pad, p, NULL);
  gst_object_unref (pad);
  return TRUE;
}

int
main (int argc, char **argv)
{
  Probe pr = { 0 };
  GError *err = NULL;
  GstBus *bus;
  int i;

  gst_init (&argc, &argv);
  if (argc < 3) {
    g_printerr ("вжиток: %s \"<опис конвеєра>\" елемент:пад [елемент:пад ...]\n",
                argv[0]);
    return 1;
  }

  g_mutex_init (&pr.lock);
  pr.contract = pr.ceiling = GST_CLOCK_TIME_NONE;
  pr.pipeline = gst_parse_launch (argv[1], &err);
  if (pr.pipeline == NULL) {
    g_printerr ("не склався конвеєр: %s\n", err->message);
    g_clear_error (&err);
    return 1;
  }
  for (i = 2; i < argc && pr.n_points < G_N_ELEMENTS (pr.pt); i++)
    if (!add_point (&pr, argv[i]))
      return 1;

  bus = gst_element_get_bus (pr.pipeline);
  gst_bus_add_watch (bus, on_bus, &pr);
  gst_object_unref (bus);

  pr.loop = g_main_loop_new (NULL, FALSE);
  g_timeout_add_seconds (2, report, &pr);

  gst_element_set_state (pr.pipeline, GST_STATE_PLAYING);
  g_main_loop_run (pr.loop);

  gst_element_set_state (pr.pipeline, GST_STATE_NULL);
  gst_object_unref (pr.pipeline);
  return 0;
}
