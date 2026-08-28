static int
run_slave (App * app, const gchar * master_host)
{
  GSocketClient *client;
  GSocketConnection *conn;
  GDataInputStream *in;
  GstClockTime base_time;
  gchar *line;
  GError *err = NULL;

  app->clock = gst_net_client_clock_new ("shared", master_host, CLOCK_PORT, 0);
  if (!app->clock) {
    g_printerr ("не створився мережевий годинник\n");
    return 1;
  }

  g_print ("підганяю годинник під %s:%d …\n", master_host, CLOCK_PORT);
  if (!gst_clock_wait_for_sync (app->clock, SYNC_TIMEOUT)) {
    g_printerr ("годинник не зійшовся за %d с — конвеєр НЕ стартує\n",
                (int) (SYNC_TIMEOUT / GST_SECOND));
    return 1;                        /* краще нічого, ніж кіно зі своєю шкалою */
  }
  g_print ("годинник зійшовся\n");

  if (!prepare_pipeline (app))
    return 1;

  client = g_socket_client_new ();
  conn = g_socket_client_connect_to_host (client, master_host, BASE_PORT, NULL, &err);
  if (!conn) {
    g_printerr ("немає TCP до майстра: %s\n", err->message);
    g_clear_error (&err);
    return 1;
  }

  in = g_data_input_stream_new (g_io_stream_get_input_stream (G_IO_STREAM (conn)));
  line = g_data_input_stream_read_line (in, NULL, NULL, &err);
  if (!line) {
    g_printerr ("майстер не віддав base_time\n");
    return 1;
  }
  base_time = g_ascii_strtoull (line, NULL, 10);
  g_free (line);
  g_object_unref (in);
  g_object_unref (conn);
  g_object_unref (client);

  start_at (app, base_time);
  g_main_loop_run (app->loop);

  return 0;
}

int
main (int argc, char **argv)
{
  App app = { 0 };
  int rc;

  gst_init (&argc, &argv);
  app.loop = g_main_loop_new (NULL, FALSE);

  if (argc >= 2 && g_str_equal (argv[1], "master"))
    rc = run_master (&app, argc > 2 ? (guint) atoi (argv[2]) : 1);
  else if (argc >= 3 && g_str_equal (argv[1], "slave"))
    rc = run_slave (&app, argv[2]);
  else {
    g_printerr ("вжиток: %s master [скільки-підлеглих]\n"
                "        %s slave <адреса-майстра>\n", argv[0], argv[0]);
    rc = 2;
  }

  if (app.pipeline) {
    gst_element_set_state (app.pipeline, GST_STATE_NULL);
    gst_object_unref (app.pipeline);
  }
  return rc;
}
