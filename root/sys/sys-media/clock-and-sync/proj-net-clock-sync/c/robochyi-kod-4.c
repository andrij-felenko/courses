static void
release_everyone (App * app)
{
  GstClockTime base_time = gst_clock_get_time (app->clock) + START_DELAY;
  gchar *line = g_strdup_printf ("%" G_GUINT64_FORMAT "\n", base_time);
  GList *l;

  for (l = app->pending; l; l = l->next) {
    GOutputStream *out = g_io_stream_get_output_stream (G_IO_STREAM (l->data));
    g_output_stream_write_all (out, line, strlen (line), NULL, NULL, NULL);
    g_output_stream_flush (out, NULL, NULL);
    g_object_unref (l->data);        /* остання посилка — GIO закриє з'єднання */
  }
  g_list_free (app->pending);
  app->pending = NULL;
  g_free (line);

  start_at (app, base_time);
}

static gboolean
on_slave_connected (GSocketService * svc, GSocketConnection * conn,
                    GObject * src, gpointer data)
{
  App *app = data;

  /* Підлеглий стукає лише після того, як його годинник зійшовся,
     тож саме з'єднання і є оголошенням готовності. */
  app->pending = g_list_prepend (app->pending, g_object_ref (conn));
  g_print ("підлеглий на зв'язку (%u з %u)\n", g_list_length (app->pending), app->want);

  if (g_list_length (app->pending) >= app->want)
    release_everyone (app);

  return TRUE;                       /* з'єднання тримаємо ми, не GIO */
}

static int
run_master (App * app, guint want)
{
  GstNetTimeProvider *provider;
  GSocketService *svc;
  GError *err = NULL;

  app->clock = gst_system_clock_obtain ();
  app->want = want;

  /* NULL як адреса = слухати на всіх інтерфейсах. */
  provider = gst_net_time_provider_new (app->clock, NULL, CLOCK_PORT);
  if (!provider) {
    g_printerr ("не піднявся постачальник часу на UDP :%d\n", CLOCK_PORT);
    return 1;
  }

  svc = g_socket_service_new ();
  if (!g_socket_listener_add_inet_port (G_SOCKET_LISTENER (svc), BASE_PORT, NULL, &err)) {
    g_printerr ("не слухається TCP :%d — %s\n", BASE_PORT, err->message);
    g_clear_error (&err);
    return 1;
  }
  g_signal_connect (svc, "incoming", G_CALLBACK (on_slave_connected), app);
  g_socket_service_start (svc);

  /* Виклики GIO прийдуть лише з головного циклу, тож прерол устигне
     завершитися раніше, ніж перший підлеглий когось розбудить. */
  if (!prepare_pipeline (app))
    return 1;

  g_print ("майстер готовий, чекаю на підлеглих: %u\n", want);
  g_main_loop_run (app->loop);

  gst_object_unref (provider);
  return 0;
}
