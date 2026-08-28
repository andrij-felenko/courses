static gboolean
on_bus_message (GstBus *bus, GstMessage *msg, gpointer user_data)
{
  Driver *d = user_data;

  handle_message (d, msg);
  if (d->quit)
    g_main_loop_quit (d->loop);    /* до Driver додано поле GMainLoop *loop */

  return TRUE;                     /* TRUE — стежити далі */
}

/* у main — замість власного циклу з gst_bus_timed_pop_filtered: */
  guint watch_id = gst_bus_add_watch (d.bus, on_bus_message, &d);

  d.loop = g_main_loop_new (NULL, FALSE);
  g_main_loop_run (d.loop);        /* без цього рядка обробник не викличеться ніколи */

  g_source_remove (watch_id);
  g_main_loop_unref (d.loop);
