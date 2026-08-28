#include <gst/gst.h>

typedef struct {
  GstElement *pipeline;
  GstBus     *bus;
  GMainLoop  *loop;
  guint       watch_id;

  GstState    target;      /* чого ми хочемо; буферизація цього не змінює */
  gboolean    is_live;     /* живий конвеєр: паузою не керуємо взагалі */
  gboolean    buffering;   /* зараз усередині набору запасу */
  int         exit_code;
} App;

/* Ім'я джерела повідомлення. Джерела може й не бути — тоді GST_OBJECT_NAME
   впаде на нульовому вказівнику, тому питаємо обережно. */
static const gchar *src_name (GstMessage *msg)
{
  GstObject *src = GST_MESSAGE_SRC (msg);
  return src ? GST_OBJECT_NAME (src) : "(без джерела)";
}

/* Обидва колбеки означено нижче; у файлі вони йдуть перед build(). */
static void     on_pad_added   (GstElement *dec, GstPad *pad, gpointer data);
static gboolean on_bus_message (GstBus *bus, GstMessage *msg, gpointer data);

static gboolean build (App *app, const gchar *uri)
{
  app->loop     = g_main_loop_new (NULL, FALSE);
  app->target   = GST_STATE_PLAYING;
  app->pipeline = gst_pipeline_new ("player");

  GstElement *dec = gst_element_factory_make ("uridecodebin", "dec");
  if (!dec) {
    g_printerr ("немає елемента uridecodebin — не встановлено gst-plugins-base\n");
    return FALSE;
  }
  g_object_set (dec, "uri", uri,
                     "use-buffering", TRUE,     /* без цього BUFFERING не постить */
                     NULL);
  gst_bin_add (GST_BIN (app->pipeline), dec);
  g_signal_connect (dec, "pad-added", G_CALLBACK (on_pad_added), app);

  app->bus      = gst_element_get_bus (app->pipeline);
  app->watch_id = gst_bus_add_watch (app->bus, on_bus_message, app);
  if (app->watch_id == 0) {
    g_printerr ("стеження не приєдналося: на шині вже є інше\n");
    return FALSE;
  }
  return TRUE;
}
