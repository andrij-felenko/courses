/* gstdiag.c — діагностична обв'язка. Чіпляється до будь-якого конвеєра
   й мовчить, доки все добре. */

#include <gst/gst.h>
#include <gst/pbutils/pbutils.h>   /* розпізнавання повідомлень про брак плагіна */
#include <glib/gstdio.h>           /* g_mkdir_with_parents() */

typedef struct {
  GstElement *pipeline;
  GstBus     *bus;
  guint       watch_id;    /* джерело подій шини в головному циклі */
  guint       guard_id;    /* сторожовий таймер; 0 — знято */
  guint       guard_sec;   /* скільки секунд чекати на PLAYING */
  const gchar *tag;        /* префікс імен dot-файлів */
  gboolean    is_live;     /* джерело живе: прероллу не буде за визначенням */
  gint64      qos_last;    /* коли востаннє друкували QoS, монотонні мкс */
} Diag;

static gboolean diag_bus   (GstBus *bus, GstMessage *msg, gpointer data);
static gboolean diag_guard (gpointer data);

/* Повний шлях елемента в графі, як його друкує сам GStreamer:
   /GstPipeline:pipeline0/GstQTDemux:qtdemux0. Звільняє викликач. */
static gchar *src_path (GstMessage *msg)
{
  GstObject *src = GST_MESSAGE_SRC (msg);
  return src ? gst_object_get_path_string (src) : g_strdup ("(без джерела)");
}

/* Знімок графа з часовою міткою в імені. */
static void diag_dump (Diag *d, const gchar *why)
{
#ifdef GST_DISABLE_GST_DEBUG
  (void) d; (void) why;
  g_printerr ("  графа не буде: бібліотеку зібрано без діагностики\n");
#else
  gchar *name = g_strdup_printf ("%s-%s", d->tag, why);
  GST_DEBUG_BIN_TO_DOT_FILE_WITH_TS (GST_BIN (d->pipeline),
                                     GST_DEBUG_GRAPH_SHOW_ALL, name);
  g_printerr ("  граф скинуто: $GST_DEBUG_DUMP_DOT_DIR/<час>-%s.dot\n", name);
  g_free (name);
#endif
}

void diag_attach (Diag *d, GstElement *pipeline, const gchar *tag, guint guard_sec)
{
  d->pipeline  = gst_object_ref (pipeline);
  d->bus       = gst_element_get_bus (pipeline);
  d->tag       = tag;
  d->guard_sec = guard_sec;

  d->watch_id = gst_bus_add_watch (d->bus, diag_bus, d);
  if (d->watch_id == 0)
    g_printerr ("на шині вже висить чуже стеження — діагностика НЕ приєдналася\n");

  if (guard_sec > 0)
    d->guard_id = g_timeout_add_seconds (guard_sec, diag_guard, d);
}

void diag_detach (Diag *d)
{
  if (d->guard_id) { g_source_remove (d->guard_id);   d->guard_id = 0; }
  if (d->watch_id) { gst_bus_remove_watch (d->bus);   d->watch_id = 0; }
  if (d->bus)      { gst_object_unref (d->bus);       d->bus      = NULL; }
  if (d->pipeline) { gst_object_unref (d->pipeline);  d->pipeline = NULL; }
}
