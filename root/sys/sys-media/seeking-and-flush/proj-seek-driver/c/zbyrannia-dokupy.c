int
main (int argc, char **argv)
{
  Player p = { 0 };
  const gchar *mode, *uri;
  int rc = 0;

  gst_init (&argc, &argv);
  if (argc < 3) {
    g_printerr ("вжиток: %s goto|compare|scrub|loop <uri> [аргументи]\n", argv[0]);
    return 2;
  }
  mode = argv[1];
  uri  = argv[2];

  p.pipeline = gst_element_factory_make ("playbin", "player");
  g_object_set (p.pipeline, "uri", uri, NULL);
  p.bus = gst_element_get_bus (p.pipeline);

  if (!bring_to_paused (&p) || !probe_seekable (&p)) {
    g_printerr ("це джерело не перемотується\n");
    rc = 1;
    goto out;
  }
  g_print ("матеріал %" GST_TIME_FORMAT "; перемотування дозволене "
           "від %" GST_TIME_FORMAT " до %" GST_TIME_FORMAT "\n",
           GST_TIME_ARGS (p.duration), GST_TIME_ARGS (p.lo), GST_TIME_ARGS (p.hi));

  if (!g_strcmp0 (mode, "goto") && argc > 3) {
    gint64 target = (gint64) (g_ascii_strtod (argv[3], NULL) * GST_SECOND);
    gint64 spent;
    SeekResult r = seek_and_wait (&p, target,
                                  GST_SEEK_FLAG_FLUSH | GST_SEEK_FLAG_ACCURATE,
                                  &spent);

    g_print ("%s за %.1f мс; позиція %" GST_TIME_FORMAT "\n",
             seek_result_name (r), spent / 1000.0,
             GST_TIME_ARGS (position_now (&p)));
    rc = (r == SEEK_OK) ? 0 : 1;

  } else if (!g_strcmp0 (mode, "compare") && argc > 3) {
    compare_accuracy (&p, (gint64) (g_ascii_strtod (argv[3], NULL) * GST_SECOND));

  } else if (!g_strcmp0 (mode, "scrub")) {
    Scrubber s = { 0 };

    s.p = &p;
    s.loop = g_main_loop_new (NULL, FALSE);
    s.moves_left = 40;
    gst_bus_add_watch (p.bus, scrub_bus, &s);
    g_timeout_add (50, scrub_tick, &s);
    g_main_loop_run (s.loop);
    gst_bus_remove_watch (p.bus);
    g_main_loop_unref (s.loop);

  } else if (!g_strcmp0 (mode, "loop") && argc > 4) {
    Looper l = { 0 };

    l.p = &p;
    l.loop = g_main_loop_new (NULL, FALSE);
    l.from = (gint64) (g_ascii_strtod (argv[3], NULL) * GST_SECOND);
    l.to   = (gint64) (g_ascii_strtod (argv[4], NULL) * GST_SECOND);
    l.laps_left = 3;
    gst_bus_add_watch (p.bus, loop_bus, &l);
    if (loop_start (&l))
      gst_element_set_state (p.pipeline, GST_STATE_PLAYING);
    g_main_loop_run (l.loop);
    gst_bus_remove_watch (p.bus);
    g_main_loop_unref (l.loop);

  } else {
    g_printerr ("невідомий режим або бракує аргументів\n");
    rc = 2;
  }

out:
  gst_element_set_state (p.pipeline, GST_STATE_NULL);
  gst_object_unref (p.bus);
  gst_object_unref (p.pipeline);
  return rc;
}
