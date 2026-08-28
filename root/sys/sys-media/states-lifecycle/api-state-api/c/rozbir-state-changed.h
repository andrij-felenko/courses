case GST_MESSAGE_STATE_CHANGED: {
  GstState old_state, new_state, pending;

  /* цих повідомлень багато — від кожного елемента;
     стан конвеєра описує лише те, що постив сам конвеєр */
  if (GST_MESSAGE_SRC (msg) != GST_OBJECT (pipeline))
    break;

  gst_message_parse_state_changed (msg, &old_state, &new_state, &pending);
  g_print ("конвеєр: %s → %s (попереду %s)\n",
      gst_element_state_get_name (old_state),
      gst_element_state_get_name (new_state),
      gst_element_state_get_name (pending));
  break;
}
