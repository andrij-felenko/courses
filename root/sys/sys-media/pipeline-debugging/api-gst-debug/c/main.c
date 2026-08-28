static void my_log (GstDebugCategory *cat, GstDebugLevel level,
                    const gchar *file, const gchar *function, gint line,
                    GObject *object, GstDebugMessage *message, gpointer data)
{
  syslog (LOG_DEBUG, "%s %s:%d %s",
          gst_debug_category_get_name (cat), file, line,
          gst_debug_message_get (message));
}

gst_debug_remove_log_function (gst_debug_log_default);
gst_debug_add_log_function (my_log, NULL, NULL);
gst_debug_set_threshold_from_string ("2,GST_STATES:5", TRUE);
