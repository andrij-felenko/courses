  /* лише для конвеєра, що пише файл */
  GstMessage *last;

  gst_element_send_event (d.pipeline, gst_event_new_eos ());

  last = gst_bus_timed_pop_filtered (d.bus, 5 * GST_SECOND,
                                     GST_MESSAGE_EOS | GST_MESSAGE_ERROR);
  if (last)
    gst_message_unref (last);

  gst_element_set_state (d.pipeline, GST_STATE_NULL);
