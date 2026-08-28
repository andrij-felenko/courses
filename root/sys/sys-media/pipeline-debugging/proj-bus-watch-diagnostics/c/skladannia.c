/* Тека для графів. Викликати ДО gst_init() — саме там читається змінна. */
static void diag_setup_dot_dir (const gchar *dir)
{
  g_mkdir_with_parents (dir, 0755);      /* GStreamer теку НЕ створює */
  g_setenv ("GST_DEBUG_DUMP_DOT_DIR", dir, TRUE);
}

int main (int argc, char **argv)
{
  if (argc < 2) {
    g_printerr ("вжиток: %s \"<опис конвеєра для gst-launch>\"\n", argv[0]);
    return 2;
  }

  diag_setup_dot_dir ("/tmp/gstdiag");   /* ПЕРЕД gst_init */
  gst_init (&argc, &argv);

  GError *perr = NULL;
  GstElement *pipeline = gst_parse_launch (argv[1], &perr);
  if (!pipeline) {
    g_printerr ("конвеєр не розібрано: %s\n", perr->message);
    g_clear_error (&perr);
    return 1;
  }

  GMainLoop *loop = g_main_loop_new (NULL, FALSE);
  Diag diag = { 0 };
  diag_attach (&diag, pipeline, "cam0", 10);   /* сторож на 10 секунд */

  if (diag_start (&diag))
    g_main_loop_run (loop);                    /* без цього рядка обв'язка мертва */

  gst_element_set_state (pipeline, GST_STATE_NULL);
  diag_detach (&diag);
  gst_object_unref (pipeline);
  g_main_loop_unref (loop);
  return 0;
}
