/* Один кадр уперед, конвеєр лишається в PAUSED. flush=TRUE обов'язковий:
   приймач тримає наповнений кадр, і без скидання крок нікуди не зрушить.
   intermediate=FALSE каже наповнитися після кроку, тобто показати те,
   на що ступили. */
static gboolean
step_one_frame (Player *p)
{
  GstMessage *msg;
  gboolean ok = FALSE;

  drain_stale (p);
  if (!gst_element_send_event (p->pipeline,
          gst_event_new_step (GST_FORMAT_BUFFERS, 1, 1.0, TRUE, FALSE)))
    return FALSE;

  msg = gst_bus_timed_pop_filtered (p->bus, SEEK_TIMEOUT,
            GST_MESSAGE_STEP_DONE | GST_MESSAGE_ERROR);
  if (msg && GST_MESSAGE_TYPE (msg) == GST_MESSAGE_STEP_DONE) {
    GstFormat fmt;
    guint64   amount, duration;
    gdouble   rate;
    gboolean  flush, intermediate, eos;

    gst_message_parse_step_done (msg, &fmt, &amount, &rate, &flush,
                                 &intermediate, &duration, &eos);
    g_print ("ступили на %" GST_TIME_FORMAT " матеріалу%s\n",
             GST_TIME_ARGS (duration), eos ? " (уперлися в кінець)" : "");
    ok = !eos;
  }
  if (msg)
    gst_message_unref (msg);
  return ok;
}
