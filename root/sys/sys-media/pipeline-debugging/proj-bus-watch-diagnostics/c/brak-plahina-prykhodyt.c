    case GST_MESSAGE_ELEMENT:
      if (gst_is_missing_plugin_message (msg)) {
        gchar *desc = gst_missing_plugin_message_get_description (msg);
        gchar *inst = gst_missing_plugin_message_get_installer_detail (msg);
        g_printerr ("БРАКУЄ ПЛАГІНА: %s\n", desc ? desc : "(без опису)");
        g_printerr ("  рядок для встановлювача: %s\n", inst ? inst : "(немає)");
        g_free (desc);   /* обидві функції віддають щойно виділені рядки */
        g_free (inst);
        diag_dump (d, "missing-plugin");
      }
      break;
