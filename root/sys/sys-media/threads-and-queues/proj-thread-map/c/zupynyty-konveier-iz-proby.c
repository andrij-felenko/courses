/* Виконується вже в чужій нитці з пулу — тут можна все. */
static void
stop_now (GstElement *pipeline, gpointer user_data)
{
  gst_element_send_event (pipeline, gst_event_new_eos ());
}

/* А ця проба лишається на паді й рахує кадри. */
static GstPadProbeReturn
count_frames (GstPad *pad, GstPadProbeInfo *info, gpointer user_data)
{
  static gint n = 0;

  if (g_atomic_int_add (&n, 1) == 99)
    gst_element_call_async (GST_ELEMENT (user_data), stop_now, NULL, NULL);

  return GST_PAD_PROBE_OK;
}
