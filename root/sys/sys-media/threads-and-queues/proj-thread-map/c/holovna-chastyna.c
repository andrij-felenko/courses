static void
dump_one_state (GstElement *e)
{
  GstState cur, pending;

  gst_element_get_state (e, &cur, &pending, 0);
  g_print ("  %-36s %-8s → %-12s%s\n", GST_OBJECT_NAME (e),
           gst_element_state_get_name (cur),
           gst_element_state_get_name (pending),
           pending != GST_STATE_VOID_PENDING ? "  ← ось хто не доїхав" : "");
}

static void
print_map (void)
{
  gint t;
  guint i;

  g_mutex_lock (&log_lock);
  g_print ("\n=== мапа ниток: %u падів у %d нитках ===\n", marks->len, next_tid - 1);
  for (t = 1; t < next_tid; t++) {
    guint own = 0;

    g_print ("\nT%d  (%p)\n", t, (void *) thr[t]);
    for (i = 0; i < marks->len; i++) {
      Mark *m = &g_array_index (marks, Mark, i);

      if (m->tid != t)
        continue;
      g_print ("    %-36s %c %s\n", m->elem, m->dir, m->pad);
      own++;
    }
    if (own == 0)
      g_print ("    (жодного пада — через цю нитку дані не течуть)\n");
  }
  g_mutex_unlock (&log_lock);
}

int
main (int argc, char *argv[])
{
  const gchar *with_queue =
      "videotestsrc num-buffers=300 ! tee name=t "
      "t. ! queue ! autovideosink "
      "t. ! queue ! jpegenc ! fakesink";
  const gchar *no_queue =
      "videotestsrc num-buffers=300 ! tee name=t "
      "t. ! autovideosink "
      "t. ! jpegenc ! fakesink";
  gboolean bare = (argc > 1 && g_strcmp0 (argv[1], "--no-queue") == 0);
  GError *err = NULL;
  GstElement *pipeline;
  GstBus *bus;
  GstStateChangeReturn ret;
  guint i;

  gst_init (&argc, &argv);
  g_mutex_init (&log_lock);
  marks = g_array_new (FALSE, FALSE, sizeof (Mark));
  tids  = g_hash_table_new (NULL, NULL);

  pipeline = gst_parse_launch (bare ? no_queue : with_queue, &err);
  if (pipeline == NULL) {
    g_printerr ("конвеєр не зібрався: %s\n", err->message);
    return 1;
  }

  bus = gst_element_get_bus (pipeline);
  gst_bus_set_sync_handler (bus, on_message_sync, NULL, NULL);

  g_mutex_lock (&log_lock);
  g_print ("нитка застосунку: T%d (%p)\n\n",
           thread_number (g_thread_self ()), (void *) g_thread_self ());
  g_mutex_unlock (&log_lock);

  /* READY, а не одразу PAUSED: у READY autovideosink уже обрав справжній
     стік і має всі пади, але жодного буфера ще не було. */
  if (gst_element_set_state (pipeline, GST_STATE_READY) == GST_STATE_CHANGE_FAILURE) {
    g_printerr ("не піднявся навіть у READY\n");
    return 1;
  }
  for_each_element (pipeline, probe_pads);

  gst_element_set_state (pipeline, GST_STATE_PLAYING);

  /* Чекаємо з обмеженням, а не назавжди: різницю між робочим конвеєром
     і зависанням видно саме тут. */
  ret = gst_element_get_state (pipeline, NULL, NULL, 5 * GST_SECOND);
  if (ret == GST_STATE_CHANGE_ASYNC) {
    g_print ("\n!! за 5 с конвеєр не дійшов до PLAYING. Стани елементів:\n");
    dump_one_state (pipeline);
    for_each_element (pipeline, dump_one_state);
  } else {
    g_usleep (500 * 1000);
    print_map ();
  }

  gst_element_set_state (pipeline, GST_STATE_NULL);

  for (i = 0; i < marks->len; i++) {
    Mark *m = &g_array_index (marks, Mark, i);
    g_free (m->elem);
    g_free (m->pad);
  }
  g_array_free (marks, TRUE);
  g_hash_table_destroy (tids);
  gst_object_unref (bus);
  gst_object_unref (pipeline);
  return 0;
}
