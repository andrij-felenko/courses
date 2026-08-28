/* autoplug.c — керований автодобір: журнал кандидатів і вето на декодер.
 *   зібрати:   gcc autoplug.c -o autoplug \
 *                  $(pkg-config --cflags --libs gstreamer-1.0 gstreamer-pbutils-1.0)
 *   запустити: ./autoplug кіно.mkv --skip=vah264dec
 *              ./autoplug https://приклад.org/кіно.webm --no-hw
 */
#include <gst/gst.h>
#include <gst/pbutils/pbutils.h>
#include <string.h>

/* Перелічення з gst/playback/gstplay-enum.h. Заголовків плагінів не
   встановлюють, тому значення переписано сюди — вони частина інтерфейсу. */
typedef enum {
  GST_AUTOPLUG_SELECT_TRY,      /* 0 — пробуй цю фабрику */
  GST_AUTOPLUG_SELECT_EXPOSE,   /* 1 — нічого не став, виставляй пад як є */
  GST_AUTOPLUG_SELECT_SKIP      /* 2 — пропусти й бери наступну */
} GstAutoplugSelectResult;

typedef struct {
  GstElement *pipeline;
  GstElement *decoder;      /* decodebin або uridecodebin */
  GMainLoop  *loop;

  gchar     **veto;         /* префікси імен, які пропускаємо */
  gboolean    no_hw;        /* пропускати все з класу Hardware */

  GMutex      lock;         /* журнал пишуть потоки даних */
  GString    *journal;
  gint        n_try, n_skip, n_branches;   /* лічильники — атомарні */

  gchar      *missing;      /* людський опис того, чого бракує */
  int         exit_code;
} App;

static GstAutoplugSelectResult on_autoplug_select (GstElement *bin, GstPad *pad,
    GstCaps *caps, GstElementFactory *factory, gpointer data);
static void     on_pad_added     (GstElement *dec, GstPad *pad, gpointer data);
static void     on_no_more_pads  (GstElement *dec, gpointer data);
static void     on_unknown_type  (GstElement *dec, GstPad *pad, GstCaps *caps, gpointer data);
static gboolean on_bus           (GstBus *bus, GstMessage *msg, gpointer data);

int
main (int argc, char *argv[])
{
  App app = { 0 };
  GPtrArray *veto = g_ptr_array_new ();
  const gchar *target = NULL;
  GstBus *bus;

  gst_init (&argc, &argv);

  for (int i = 1; i < argc; i++) {
    if (g_str_has_prefix (argv[i], "--skip="))
      g_ptr_array_add (veto, argv[i] + strlen ("--skip="));   /* рядки з argv, не наші */
    else if (g_strcmp0 (argv[i], "--no-hw") == 0)
      app.no_hw = TRUE;
    else
      target = argv[i];
  }
  g_ptr_array_add (veto, NULL);
  app.veto = (gchar **) veto->pdata;

  if (!target) {
    g_printerr ("вжиток: %s <файл|URI> [--skip=ім'я]… [--no-hw]\n", argv[0]);
    return 1;
  }

  g_mutex_init (&app.lock);
  app.journal  = g_string_new (NULL);
  app.loop     = g_main_loop_new (NULL, FALSE);
  app.pipeline = gst_pipeline_new ("autoplug");

  if (gst_uri_is_valid (target)) {
    app.decoder = gst_element_factory_make ("uridecodebin", "dec");
    g_object_set (app.decoder, "uri", target, NULL);
    gst_bin_add (GST_BIN (app.pipeline), app.decoder);
  } else {
    GstElement *src = gst_element_factory_make ("filesrc", NULL);
    app.decoder = gst_element_factory_make ("decodebin", "dec");
    g_object_set (src, "location", target, NULL);
    gst_bin_add_many (GST_BIN (app.pipeline), src, app.decoder, NULL);
    if (!gst_element_link (src, app.decoder))
      g_error ("filesrc → decodebin не з'єдналися");
  }

  /* Три точки втручання плюс окремий сигнал на випадок «нема чим декодувати».
     G_CONNECT_AFTER до autoplug-select чіпляти НЕ МОЖНА: такий обробник
     не викличуть ніколи. */
  g_signal_connect (app.decoder, "autoplug-select", G_CALLBACK (on_autoplug_select), &app);
  g_signal_connect (app.decoder, "pad-added",       G_CALLBACK (on_pad_added), &app);
  g_signal_connect (app.decoder, "no-more-pads",    G_CALLBACK (on_no_more_pads), &app);
  g_signal_connect (app.decoder, "unknown-type",    G_CALLBACK (on_unknown_type), &app);

  bus = gst_element_get_bus (app.pipeline);
  gst_bus_add_watch (bus, on_bus, &app);      /* вартовий працює в головному потоці */
  gst_object_unref (bus);

  gst_element_set_state (app.pipeline, GST_STATE_PLAYING);
  g_main_loop_run (app.loop);
  gst_element_set_state (app.pipeline, GST_STATE_NULL);

  g_print ("\n── журнал автодобору ────────────────────────\n%s", app.journal->str);
  g_print ("спроб дозволено: %d, пропущено: %d, гілок під'єднано: %d\n",
           g_atomic_int_get (&app.n_try), g_atomic_int_get (&app.n_skip),
           g_atomic_int_get (&app.n_branches));

  gst_object_unref (app.pipeline);
  g_main_loop_unref (app.loop);
  g_string_free (app.journal, TRUE);
  g_mutex_clear (&app.lock);
  g_free (app.missing);
  g_ptr_array_free (veto, TRUE);
  return app.exit_code;
}
