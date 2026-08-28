static void finish_stop_recording(App *a);

static gboolean on_rec_deadline(gpointer user)
{
    App *a = user;
    g_printerr("пакувальник мовчить 3 с — знімаємо силою, файл може бути битий\n");
    a->rec_deadline = 0;
    finish_stop_recording(a);
    return G_SOURCE_REMOVE;
}

static void stop_recording(App *a)
{
    if (!a->rec_sink || a->rec_closing) return;

    /* 1 · клапан: нові кадри в гілку більше не заходять */
    g_object_set(a->rec_valve, "drop", TRUE, NULL);

    /* 2 · від'єднати пакувальник від решти гілки */
    GstPad *src  = gst_element_get_static_pad(a->rec_valve, "src");
    GstPad *sink = gst_pad_get_peer(src);        /* запитаний пад "video" пакувальника */
    gst_pad_unlink(src, sink);
    gst_object_unref(src);

    /* 3 · подія кінця потоку — ПРЯМО в пад пакувальника.
           Через клапан вона б не пройшла: закритий клапан їсть і події. */
    a->rec_closing = TRUE;
    if (!gst_pad_send_event(sink, gst_event_new_eos()))
        g_printerr("подія кінця потоку не дійшла\n");
    gst_object_unref(sink);

    /* 4 · чекаємо підтвердження — але не вічно */
    a->rec_deadline = g_timeout_add_seconds(3, on_rec_deadline, a);
}

/* 5 · прибирання. Викликається з головної нитки, коли файл уже закрито. */
static void finish_stop_recording(App *a)
{
    if (!a->rec_closing) return;
    a->rec_closing = FALSE;

    if (a->rec_deadline) { g_source_remove(a->rec_deadline); a->rec_deadline = 0; }

    gst_element_set_state(a->rec_sink, GST_STATE_NULL);
    gst_element_get_state(a->rec_sink, NULL, NULL, GST_CLOCK_TIME_NONE);
    gst_bin_remove(GST_BIN(a->pipeline), a->rec_sink);   /* контейнер віддає посилання */
    a->rec_sink = NULL;
}
