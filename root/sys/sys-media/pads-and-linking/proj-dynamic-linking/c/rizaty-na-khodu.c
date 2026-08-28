/* Виконується в потоці з пулу GStreamer — не в streaming-потоці.
   Тут уже можна змінювати стани. */
static void
teardown_video_branch (GstElement *pipeline, gpointer user_data)
{
  App *app = user_data;

  gst_element_set_state (app->video_branch, GST_STATE_NULL);
  gst_bin_remove (GST_BIN (pipeline), app->video_branch);  /* конвеєр відпускає своє посилання */
  app->video_branch = NULL;

  gst_object_unref (app->video_pad);
  app->video_pad = NULL;

  g_print ("відеогілку вилучено, звук грає далі\n");
}

/* Проба IDLE: GStreamer кличе її, коли через пад ТОЧНО нічого не тече. */
static GstPadProbeReturn
on_pad_idle (GstPad *pad, GstPadProbeInfo *info, gpointer user_data)
{
  App *app = user_data;

  /* У пробу можна ввійти двічі: негайно, з потоку, який її ставив (якщо пад
     уже був порожній), і зі streaming-потоку. Ріжемо рівно один раз. */
  if (!g_atomic_int_compare_and_exchange (&app->cut_started, 0, 1))
    return GST_PAD_PROBE_REMOVE;

  GstPad *branch_in = gst_pad_get_peer (pad);
  if (branch_in != NULL) {
    gst_pad_unlink (pad, branch_in);       /* розрив дешевий: два покажчики */
    gst_object_unref (branch_in);
  }

  /* set_state(NULL) звідси означало б зупиняти потік, у якому ми стоїмо.
     Тому решту роботи віддаємо чужому потокові. */
  gst_element_call_async (app->pipeline, teardown_video_branch, app, NULL);

  return GST_PAD_PROBE_REMOVE;             /* проба знімає себе, пад вільний */
}

/* Головний потік, за таймером. */
static gboolean
cut_video_branch (gpointer user_data)
{
  App *app = user_data;

  if (app->video_pad != NULL)
    gst_pad_add_probe (app->video_pad, GST_PAD_PROBE_TYPE_IDLE,
                       on_pad_idle, app, NULL);
  return G_SOURCE_REMOVE;                  /* таймер одноразовий */
}
