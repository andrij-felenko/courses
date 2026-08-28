static GstPadProbeReturn
on_buffer (GstPad *pad, GstPadProbeInfo *info, gpointer user_data)
{
  Driver *d = user_data;
  static guint frames = 0;         /* проба одна — статичний лічильник тут доречний */

  if (++frames < 300)
    return GST_PAD_PROBE_OK;

  /* НЕ gst_element_set_state (...), а повідомлення на шину */
  gst_element_post_message (d->pipeline,
      gst_message_new_application (GST_OBJECT (d->pipeline),
          gst_structure_new_empty ("app-stop")));

  return GST_PAD_PROBE_REMOVE;     /* більше нас не турбувати */
}
