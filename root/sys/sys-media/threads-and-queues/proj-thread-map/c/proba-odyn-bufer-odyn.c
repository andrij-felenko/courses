/* Спрацьовує на ПЕРШОМУ буфері цього пада й одразу знімає себе.
   Виконується в нитці потоку, із узятим замком потоку — тому тут
   дозволено рівно два рухи: узяти імена й надрукувати рядок. */
static GstPadProbeReturn
first_buffer (GstPad *pad, GstPadProbeInfo *info, gpointer user_data)
{
  GstElement *owner = gst_pad_get_parent_element (pad);
  Mark m;

  m.thread = g_thread_self ();
  m.elem   = owner ? gst_element_get_name (owner) : g_strdup ("?");
  m.pad    = gst_pad_get_name (pad);
  m.dir    = (GST_PAD_DIRECTION (pad) == GST_PAD_SINK) ? '<' : '>';

  g_mutex_lock (&log_lock);
  m.tid = thread_number (m.thread);
  g_array_append_val (marks, m);
  g_print ("  T%-2d  %-34s %c %s\n", m.tid, m.elem, m.dir, m.pad);
  g_mutex_unlock (&log_lock);

  if (owner)
    gst_object_unref (owner);

  return GST_PAD_PROBE_REMOVE;   /* нас цікавив ЛИШЕ перший буфер */
}
