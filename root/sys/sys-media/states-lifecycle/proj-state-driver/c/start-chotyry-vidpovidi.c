int
main (int argc, char *argv[])
{
  Driver d = { NULL, NULL, FALSE, FALSE, FALSE };
  GError *err = NULL;
  GstStateChangeReturn ret;
  int rc = 0;

  gst_init (&argc, &argv);

  if (argc < 2) {
    g_printerr ("вжиток: %s \"<опис конвеєра>\"\n", argv[0]);
    return 2;
  }

  d.pipeline = gst_parse_launch (argv[1], &err);
  if (d.pipeline == NULL) {
    g_printerr ("конвеєр не зібрано: %s\n", err ? err->message : "причина невідома");
    g_clear_error (&err);
    return 2;
  }
  if (err != NULL) {               /* зібрався, але не без зауважень */
    g_printerr ("зауваження при зборі: %s\n", err->message);
    g_clear_error (&err);
  }

  d.bus = gst_element_get_bus (d.pipeline);

  /* Крок 1: у PAUSED — і лише тут стає видно, з чим ми маємо справу. */
  ret = gst_element_set_state (d.pipeline, GST_STATE_PAUSED);

  switch (ret) {
    case GST_STATE_CHANGE_FAILURE:
      g_printerr ("перехід у PAUSED провалився\n");
      drain_bus (&d);              /* причина вже на шині */
      rc = 1;
      goto teardown;

    case GST_STATE_CHANGE_NO_PREROLL:
      g_print ("джерело живе: наповнення не буде — не чекаємо нічого\n");
      d.is_live = TRUE;
      break;

    case GST_STATE_CHANGE_ASYNC:
      g_print ("наповнення триває — чекаємо ASYNC_DONE\n");
      if (!wait_for_async_done (&d, 10 * GST_SECOND)) {
        rc = 1;
        goto teardown;
      }
      g_print ("наповнено: конвеєр у PAUSED\n");
      break;

    case GST_STATE_CHANGE_SUCCESS:
      g_print ("PAUSED досягнуто одразу\n");
      break;
  }

  /* Наповнення (якщо воно було) дало відповіді, яких до нього не існувало. */
  if (!d.is_live) {
    gint64 duration = -1;

    if (gst_element_query_duration (d.pipeline, GST_FORMAT_TIME, &duration))
      g_print ("тривалість: %" GST_TIME_FORMAT "\n", GST_TIME_ARGS (duration));
    else
      g_print ("тривалість невідома — потік без кінця\n");
  }
