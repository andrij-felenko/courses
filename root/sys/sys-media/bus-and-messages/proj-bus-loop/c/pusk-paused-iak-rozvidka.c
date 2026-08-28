int main (int argc, char **argv)
{
  gst_init (&argc, &argv);
  if (argc < 2) {
    g_printerr ("вжиток: %s <uri>\n", argv[0]);
    return 2;
  }

  App app = { 0 };
  if (!build (&app, argv[1]))
    return 1;

  GstStateChangeReturn ret = gst_element_set_state (app.pipeline, GST_STATE_PAUSED);

  if (ret == GST_STATE_CHANGE_FAILURE) {
    /* головного циклу ще нема, забрати повідомлення нікому — беремо самі */
    GstMessage *msg = gst_bus_timed_pop_filtered (app.bus, 0, GST_MESSAGE_ERROR);
    if (msg) {
      report_error (msg);
      gst_message_unref (msg);        /* це повідомлення НАШЕ */
    } else {
      g_printerr ("конвеєр не пішов у PAUSED, а помилки на шині немає\n");
    }
    app.exit_code = 1;
  } else {
    app.is_live = (ret == GST_STATE_CHANGE_NO_PREROLL);
    gst_element_set_state (app.pipeline, GST_STATE_PLAYING);
    g_main_loop_run (app.loop);       /* уся програма живе тут */
  }

  /* однаковий шлях і після помилки, і після EOS */
  gst_element_set_state (app.pipeline, GST_STATE_NULL);
  gst_bus_remove_watch (app.bus);
  gst_object_unref (app.bus);
  gst_object_unref (app.pipeline);
  g_main_loop_unref (app.loop);
  return app.exit_code;
}
