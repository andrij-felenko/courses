static void
dump_bin (GstBin *bin, int depth)
{
  GstIterator *it = gst_bin_iterate_sorted (bin);
  GValue item = G_VALUE_INIT;
  gboolean done = FALSE;

  while (!done) {
    switch (gst_iterator_next (it, &item)) {
      case GST_ITERATOR_OK: {
        GstElement *e = g_value_get_object (&item);
        GstElementFactory *f = gst_element_get_factory (e);

        g_print ("%*s%s  (%s)\n", depth * 2, "", GST_OBJECT_NAME (e),
                 f ? gst_plugin_feature_get_name (GST_PLUGIN_FEATURE (f)) : "—");
        if (GST_IS_BIN (e))
          dump_bin (GST_BIN (e), depth + 1);
        g_value_reset (&item);
        break;
      }
      case GST_ITERATOR_RESYNC:
        gst_iterator_resync (it);       /* граф змінився під час обходу */
        break;
      default:
        done = TRUE;
        break;
    }
  }
  g_value_unset (&item);
  gst_iterator_free (it);
}

static gboolean
dump_topology (gpointer data)
{
  App *app = data;

  g_print ("\n── топологія після no-more-pads ─────────────\n");
  dump_bin (GST_BIN (app->pipeline), 0);
  return G_SOURCE_REMOVE;
}

static void
on_no_more_pads (GstElement *dec, gpointer data)
{
  /* Ми в потоці даних: віддаємо роботу головному циклу й одразу повертаємось. */
  g_idle_add (dump_topology, data);
}

static void
on_unknown_type (GstElement *dec, GstPad *pad, GstCaps *caps, gpointer data)
{
  App *app = data;
  gchar *s = gst_caps_to_string (caps);

  journal (app, "нема чим декодувати: %s", s);
  app->exit_code = 2;
  g_free (s);
}

static gboolean
on_bus (GstBus *bus, GstMessage *msg, gpointer data)
{
  App *app = data;

  switch (GST_MESSAGE_TYPE (msg)) {
    case GST_MESSAGE_ELEMENT:
      if (gst_is_missing_plugin_message (msg)) {
        gchar *desc   = gst_missing_plugin_message_get_description (msg);
        gchar *detail = gst_missing_plugin_message_get_installer_detail (msg);

        g_free (app->missing);
        app->missing = g_strdup (desc);
        g_print ("бракує: %s\n", desc);
        if (detail)
          g_print ("  рядок для встановлювача: %s\n", detail);
        g_free (desc);                 /* обидва рядки — наші, звільняємо */
        g_free (detail);
      }
      break;

    case GST_MESSAGE_ERROR: {
      GError *err = NULL;
      gchar *dbg = NULL;

      gst_message_parse_error (msg, &err, &dbg);
      g_printerr ("помилка від %s: %s\n", GST_OBJECT_NAME (msg->src), err->message);
      if (app->missing)
        g_printerr ("  найімовірніша причина: у системі немає %s\n", app->missing);
      g_clear_error (&err);
      g_free (dbg);
      app->exit_code = 1;
      g_main_loop_quit (app->loop);
      break;
    }

    case GST_MESSAGE_EOS:
      g_main_loop_quit (app->loop);
      break;

    default:
      break;
  }
  return TRUE;                        /* вартовий лишається на місці */
}
