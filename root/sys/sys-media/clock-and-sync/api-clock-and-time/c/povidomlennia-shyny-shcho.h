case GST_MESSAGE_CLOCK_LOST:
  gst_element_set_state (pipeline, GST_STATE_PAUSED);
  gst_element_set_state (pipeline, GST_STATE_PLAYING);
  break;

case GST_MESSAGE_LATENCY:
  gst_bin_recalculate_latency (GST_BIN (pipeline));
  break;

case GST_MESSAGE_NEW_CLOCK: {
  GstClock *clock;
  gst_message_parse_new_clock (msg, &clock);       /* годинник належить повідомленню */
  g_print ("годинник конвеєра: %s\n", clock ? GST_OBJECT_NAME (clock) : "немає");
  break;
}
