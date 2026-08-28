#include <gst/gst.h>

typedef struct {
  GMainLoop *loop;
  GstElement *pipeline;
  gboolean sent;
} App;

static gboolean
on_bus (GstBus *bus, GstMessage *msg, gpointer data)
{
  App *app = data;

  switch (GST_MESSAGE_TYPE (msg)) {
    case GST_MESSAGE_STREAM_COLLECTION: {
      GstStreamCollection *coll = NULL;
      gst_message_parse_stream_collection (msg, &coll);      /* transfer full */
      if (coll == NULL)
        break;

      GList *wanted = NULL;
      gboolean have_video = FALSE, have_audio = FALSE;
      guint n = gst_stream_collection_get_size (coll);

      for (guint i = 0; i < n; i++) {
        GstStream *s = gst_stream_collection_get_stream (coll, i);  /* transfer none */
        GstStreamType t = gst_stream_get_stream_type (s);
        const gchar *id = gst_stream_get_stream_id (s);

        g_print ("%u  %-9s %s\n", i, gst_stream_type_get_name (t), id);

        if (t == GST_STREAM_TYPE_VIDEO && !have_video) {
          wanted = g_list_append (wanted, (gpointer) id);
          have_video = TRUE;
        } else if (t == GST_STREAM_TYPE_AUDIO && !have_audio) {
          wanted = g_list_append (wanted, (gpointer) id);
          have_audio = TRUE;
        }
      }

      if (wanted != NULL && !app->sent) {
        app->sent = TRUE;
        gst_element_send_event (app->pipeline,
            gst_event_new_select_streams (wanted));
      }

      g_list_free (wanted);          /* самі рядки належать колекції */
      gst_object_unref (coll);
      break;
    }

    case GST_MESSAGE_STREAMS_SELECTED: {
      guint n = gst_message_streams_selected_get_size (msg);
      g_print ("обрано %u:\n", n);
      for (guint i = 0; i < n; i++) {
        GstStream *s = gst_message_streams_selected_get_stream (msg, i); /* full */
        g_print ("   %s\n", gst_stream_get_stream_id (s));
        gst_object_unref (s);
      }
      break;
    }

    case GST_MESSAGE_ERROR: {
      GError *err = NULL;
      gchar *dbg = NULL;
      gst_message_parse_error (msg, &err, &dbg);
      g_printerr ("помилка: %s\n%s\n", err->message, dbg ? dbg : "");
      g_clear_error (&err);
      g_free (dbg);
      g_main_loop_quit (app->loop);
      break;
    }

    case GST_MESSAGE_EOS:
      g_main_loop_quit (app->loop);
      break;

    default:
      break;
  }
  return TRUE;
}

int
main (int argc, char *argv[])
{
  gst_init (&argc, &argv);

  if (argc < 2) {
    g_printerr ("вжиток: %s <uri>\n", argv[0]);
    return 2;
  }

  App app = { 0, };
  app.loop = g_main_loop_new (NULL, FALSE);
  app.pipeline = gst_element_factory_make ("playbin3", "player");
  g_object_set (app.pipeline, "uri", argv[1], NULL);

  GstBus *bus = gst_element_get_bus (app.pipeline);
  gst_bus_add_watch (bus, on_bus, &app);
  gst_object_unref (bus);

  gst_element_set_state (app.pipeline, GST_STATE_PLAYING);
  g_main_loop_run (app.loop);

  gst_element_set_state (app.pipeline, GST_STATE_NULL);
  gst_object_unref (app.pipeline);
  g_main_loop_unref (app.loop);
  return 0;
}
