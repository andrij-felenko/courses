/* first-pipeline.c — той самий ланцюг, зібраний руками.
 *
 *   gcc first-pipeline.c -o first-pipeline \
 *       $(pkg-config --cflags --libs gstreamer-1.0)
 *   ./first-pipeline rtsp://192.168.1.90/stream
 */
#include <gst/gst.h>

enum { SRC, DEPAY, PARSE, DEC, CONV, QUEUE, SINK, N_EL };

static const char *FACTORY[N_EL] = {
  "rtspsrc", "rtph264depay", "h264parse", "avdec_h264",
  "videoconvert", "queue", "autovideosink"
};

typedef struct {
  GstElement *pipeline;
  GstElement *e[N_EL];
} Chain;

/* ── Замикання щілини ────────────────────────────────────────────────────
 * Виклик приходить із нитки rtspsrc — тієї, що розбирає відповідь камери.
 * Блокуватися тут надовго не можна: доки ми не повернемось, потік стоїть.  */
static void
on_pad_added (GstElement *src, GstPad *new_pad, gpointer user_data)
{
  Chain *c = user_data;
  GstPad *sink_pad;
  GstCaps *caps;
  const gchar *media = NULL, *encoding = NULL;

  sink_pad = gst_element_get_static_pad (c->e[DEPAY], "sink");   /* +1 */

  caps = gst_pad_get_current_caps (new_pad);
  if (caps == NULL)                       /* пад ще без узгодженого формату */
    caps = gst_pad_query_caps (new_pad, NULL);

  if (gst_caps_get_size (caps) > 0) {
    const GstStructure *st = gst_caps_get_structure (caps, 0);
    media    = gst_structure_get_string (st, "media");
    encoding = gst_structure_get_string (st, "encoding-name");
  }

  /* Імена падів різняться між версіями, вміст — ні: дивимося на caps.
     Для звукової доріжки тут буде media=audio — її ми не чіпаємо.        */
  if (g_strcmp0 (media, "video") != 0 || g_strcmp0 (encoding, "H264") != 0) {
    g_print ("пропускаємо потік %s/%s\n",
             media ? media : "?", encoding ? encoding : "?");
  } else if (gst_pad_is_linked (sink_pad)) {
    g_print ("відеогілку вже під'єднано, другу не чіпаємо\n");
  } else if (GST_PAD_LINK_FAILED (gst_pad_link (new_pad, sink_pad))) {
    g_printerr ("пад %s не став на вхід депейлоадера\n",
                GST_PAD_NAME (new_pad));
  } else {
    g_print ("відеогілку замкнено на паді %s\n", GST_PAD_NAME (new_pad));
  }

  gst_caps_unref (caps);              /* обидві гілки вище дали нам +1 */
  gst_object_unref (sink_pad);        /* віддаємо те, що взяли */
}

/* ── Складання ───────────────────────────────────────────────────────── */
static gboolean
build_chain (Chain *c, const char *uri)
{
  int i;

  c->pipeline = gst_pipeline_new ("cam");

  for (i = 0; i < N_EL; i++) {
    c->e[i] = gst_element_factory_make (FACTORY[i], NULL);
    if (c->e[i] == NULL) {
      g_printerr ("немає елемента «%s»: не встановлено плагін, що його дає\n",
                  FACTORY[i]);
      while (i-- > 0)         /* створене досі ще нічиє — віддати вручну */
        gst_object_unref (c->e[i]);
      return FALSE;
    }
  }

  g_object_set (c->e[SRC], "location", uri, "latency", (guint) 200, NULL);
  g_object_set (c->e[SINK], "sync", TRUE, NULL);   /* показувати за годинником */

  /* Спершу в бін: зв'язувати можна лише елементи зі спільним батьком.
     Бін забирає плавуче посилання — далі за їхнє життя відповідає він. */
  gst_bin_add_many (GST_BIN (c->pipeline),
                    c->e[SRC], c->e[DEPAY], c->e[PARSE], c->e[DEC],
                    c->e[CONV], c->e[QUEUE], c->e[SINK], NULL);

  /* Статична частина: від депейлоадера до вікна. rtspsrc сюди не входить. */
  if (!gst_element_link_many (c->e[DEPAY], c->e[PARSE], c->e[DEC],
                              c->e[CONV], c->e[QUEUE], c->e[SINK], NULL)) {
    g_printerr ("статичну частину ланцюга не вдалося зв'язати\n");
    return FALSE;
  }

  /* Підписка ДО запуску: пад з'явиться вже під час переходу в PLAYING. */
  g_signal_connect (c->e[SRC], "pad-added", G_CALLBACK (on_pad_added), c);
  return TRUE;
}

/* ── Запуск, шина, погашення ─────────────────────────────────────────── */
int
main (int argc, char *argv[])
{
  Chain c = { 0 };
  GstBus *bus = NULL;
  GstStateChangeReturn ret;
  gboolean quit = FALSE;
  int rc = 0;

  gst_init (&argc, &argv);          /* забирає свої аргументи з argv */
  if (argc < 2) {
    g_printerr ("вжиток: %s rtsp://…\n", argv[0]);
    return 1;
  }

  if (!build_chain (&c, argv[1])) { rc = 1; goto shutdown; }

  bus = gst_element_get_bus (c.pipeline);          /* +1 */

  ret = gst_element_set_state (c.pipeline, GST_STATE_PLAYING);
  if (ret == GST_STATE_CHANGE_FAILURE) {
    g_printerr ("конвеєр не рушив: не склалася вже перша сходинка\n");
    rc = 1; goto shutdown;
  }
  /* GST_STATE_CHANGE_ASYNC тут — норма: відповідь прийде в шину.
     Для живого джерела на сходинці PAUSED буває NO_PREROLL.        */

  while (!quit) {
    GstMessage *msg = gst_bus_timed_pop_filtered (
        bus, GST_CLOCK_TIME_NONE,
        GST_MESSAGE_ERROR | GST_MESSAGE_EOS | GST_MESSAGE_STATE_CHANGED);
    if (msg == NULL)
      continue;

    switch (GST_MESSAGE_TYPE (msg)) {
      case GST_MESSAGE_ERROR: {
        GError *err = NULL;
        gchar  *dbg = NULL;
        gst_message_parse_error (msg, &err, &dbg);
        g_printerr ("помилка від %s: %s\n",
                    GST_OBJECT_NAME (GST_MESSAGE_SRC (msg)), err->message);
        if (dbg)
          g_printerr ("подробиці: %s\n", dbg);
        g_clear_error (&err);
        g_free (dbg);
        rc = 1; quit = TRUE;
        break;
      }
      case GST_MESSAGE_EOS:
        g_print ("потік скінчився\n");
        quit = TRUE;
        break;
      case GST_MESSAGE_STATE_CHANGED:
        /* Стан міняють усі елементи; нас цікавить лише сам конвеєр. */
        if (GST_MESSAGE_SRC (msg) == GST_OBJECT (c.pipeline)) {
          GstState from, to;
          gst_message_parse_state_changed (msg, &from, &to, NULL);
          g_print ("конвеєр: %s → %s\n",
                   gst_element_state_get_name (from),
                   gst_element_state_get_name (to));
        }
        break;
      default:
        break;
    }
    gst_message_unref (msg);        /* повідомлення теж наше */
  }

shutdown:
  if (c.pipeline) {
    gst_element_set_state (c.pipeline, GST_STATE_NULL);  /* спершу погасити */
    gst_object_unref (c.pipeline);                       /* потім віддати */
  }
  if (bus)
    gst_object_unref (bus);
  return rc;
}
