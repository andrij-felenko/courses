static gboolean add_rec_branch(App *a)
{
    a->rec_q     = gst_element_factory_make("queue", "rec_q");
    a->rec_valve = gst_element_factory_make("valve", "rec_v");

    /* У файл мусить лягти все: черга НЕ протікає, обмежена лише часом. */
    g_object_set(a->rec_q, "leaky",            0,
                           "max-size-buffers", 0,
                           "max-size-bytes",   0,
                           "max-size-time",    (guint64) 3 * GST_SECOND,
                           NULL);
    g_object_set(a->rec_valve, "drop", TRUE, NULL);     /* запис поки вимкнено */

    gst_bin_add_many(GST_BIN(a->pipeline), a->rec_q, a->rec_valve, NULL);
    if (!gst_element_link(a->rec_q, a->rec_valve)) return FALSE;

    return link_to_tee(a, a->rec_q, NULL);
}

static void start_recording(App *a)
{
    if (a->rec_sink || a->rec_closing) return;      /* уже пишемо або ще закриваємо */

    a->rec_sink = gst_element_factory_make("splitmuxsink", "rec_sink");
    g_object_set(a->rec_sink, "location",      "flight-%05d.mp4",
                              "max-size-time", (guint64) 60 * GST_SECOND,
                              NULL);

    gst_bin_add(GST_BIN(a->pipeline), a->rec_sink);
    gst_element_link(a->rec_valve, a->rec_sink);    /* пад "video" запитається сам */

    /* Конвеєр уже грає, а новий елемент народився в стані NULL. */
    gst_element_sync_state_with_parent(a->rec_sink);

    /* Клапан відкриваємо ОСТАННІМ — інакше перші буфери прилетять
       у ще не готовий пакувальник. */
    g_object_set(a->rec_valve, "drop", FALSE, NULL);
}
