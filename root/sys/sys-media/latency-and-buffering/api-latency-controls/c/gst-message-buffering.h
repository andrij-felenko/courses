case GST_MESSAGE_BUFFERING: {
    gint percent;

    if (is_live)                 /* живий конвеєр стану НЕ міняє */
        break;

    gst_message_parse_buffering (msg, &percent);
    gst_element_set_state (pipeline,
        percent < 100 ? GST_STATE_PAUSED : GST_STATE_PLAYING);
    break;
}
