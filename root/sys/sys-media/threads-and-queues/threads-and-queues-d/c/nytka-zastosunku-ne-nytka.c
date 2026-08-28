static void
stop_pipeline (GstElement *pipeline, gpointer user_data)
{
  gst_element_set_state (pipeline, GST_STATE_NULL);   /* уже в чужій нитці — безпечно */
}

static GstPadProbeReturn
on_eos_probe (GstPad *pad, GstPadProbeInfo *info, gpointer user_data)
{
  gst_element_call_async (GST_ELEMENT (user_data), stop_pipeline, NULL, NULL);
  return GST_PAD_PROBE_OK;
}
