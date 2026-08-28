    case GST_MESSAGE_QOS: {
      gint64 now = g_get_monotonic_time ();
      if (now - d->qos_last < G_USEC_PER_SEC)
        break;                       /* не частіше ніж раз на секунду */
      d->qos_last = now;

      GstFormat fmt = GST_FORMAT_UNDEFINED;
      guint64   processed = 0, dropped = 0;
      gst_message_parse_qos_stats (msg, &fmt, &processed, &dropped);
      if (fmt == GST_FORMAT_UNDEFINED)
        break;                       /* елемент лічби не веде — рахувати нема чого */

      gint64  jitter = 0;
      gdouble proportion = 1.0;
      gint    quality = 0;
      gst_message_parse_qos_values (msg, &jitter, &proportion, &quality);

      gchar *path = src_path (msg);
      g_printerr ("QoS %s [%s]: оброблено %" G_GUINT64_FORMAT
                  ", викинуто %" G_GUINT64_FORMAT
                  "; запізнення %.1f мс, темп ×%.2f\n",
                  path, gst_format_get_name (fmt), processed, dropped,
                  jitter / 1e6, proportion);
      g_free (path);
      break;
    }
