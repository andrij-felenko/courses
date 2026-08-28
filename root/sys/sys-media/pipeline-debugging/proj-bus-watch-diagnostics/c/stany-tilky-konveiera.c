    case GST_MESSAGE_STATE_CHANGED: {
      if (GST_MESSAGE_SRC (msg) != GST_OBJECT (d->pipeline))
        break;                       /* стани окремих елементів — не наша справа */

      GstState from, to, pending;
      gst_message_parse_state_changed (msg, &from, &to, &pending);
      g_printerr ("конвеєр: %s → %s\n",
                  gst_element_state_get_name (from),
                  gst_element_state_get_name (to));

      if (to == GST_STATE_PLAYING && d->guard_id) {
        g_source_remove (d->guard_id);   /* доїхали — сторож більше не потрібен */
        d->guard_id = 0;
      }
      break;
    }
