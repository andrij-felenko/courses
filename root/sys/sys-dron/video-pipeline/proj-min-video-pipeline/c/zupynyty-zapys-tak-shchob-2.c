static gboolean on_bus(GstBus *bus, GstMessage *msg, gpointer user)
{
    App *a = user;

    switch (GST_MESSAGE_TYPE(msg)) {
    case GST_MESSAGE_ELEMENT: {
        const GstStructure *s = gst_message_get_structure(msg);
        if (a->rec_closing && s &&
            gst_structure_has_name(s, "splitmuxsink-fragment-closed")) {
            g_print("файл закрито: %s\n", gst_structure_get_string(s, "location"));
            finish_stop_recording(a);
        }
        break;
    }
    case GST_MESSAGE_ERROR: {
        GError *err = NULL; gchar *dbg = NULL;
        gst_message_parse_error(msg, &err, &dbg);
        g_printerr("помилка від %s: %s\n", GST_OBJECT_NAME(msg->src), err->message);
        g_clear_error(&err); g_free(dbg);
        g_main_loop_quit(a->loop);
        break;
    }
    default: break;
    }
    return TRUE;         /* лишаємось на шині */
}
