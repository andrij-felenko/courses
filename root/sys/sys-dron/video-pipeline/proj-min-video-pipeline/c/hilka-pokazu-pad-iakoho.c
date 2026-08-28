static void on_decode_pad(GstElement *dec, GstPad *pad, gpointer user)
{
    App *a = user;
    GstPad *in = gst_element_get_static_pad(a->convert, "sink");
    if (!gst_pad_is_linked(in))
        gst_pad_link(pad, in);
    gst_object_unref(in);
}

static gboolean add_view_branch(App *a)
{
    a->view_q     = gst_element_factory_make("queue",         "view_q");
    a->view_valve = gst_element_factory_make("valve",         "view_v");
    a->decode     = gst_element_factory_make("decodebin3",    "dec");
    a->convert    = gst_element_factory_make("videoconvert",  "conv");
    a->view_sink  = gst_element_factory_make("autovideosink", "view_sink");

    /* Свіжість дорожча за плавність: два буфери, найстаріший — за борт. */
    g_object_set(a->view_q, "max-size-buffers", 2,
                            "max-size-bytes",   0,
                            "max-size-time",    (guint64) 0,
                            "leaky",            2,   /* downstream: викидаємо старе */
                            NULL);

    g_object_set(a->view_valve, "drop",  FALSE, NULL);  /* показ одразу ввімкнено */
    g_object_set(a->view_sink,  "sync",  FALSE, NULL);  /* не тримати кадр до мітки часу */

    gst_bin_add_many(GST_BIN(a->pipeline), a->view_q, a->view_valve,
                     a->decode, a->convert, a->view_sink, NULL);

    if (!gst_element_link_many(a->view_q, a->view_valve, a->decode, NULL)) return FALSE;
    if (!gst_element_link(a->convert, a->view_sink))                       return FALSE;

    /* Вихідного пада в декодера ще немає — він з'явиться, коли той
       розбереться з форматом. Тому лінкуємо не тут, а в обробнику. */
    g_signal_connect(a->decode, "pad-added", G_CALLBACK(on_decode_pad), a);

    return link_to_tee(a, a->view_q, NULL);
}
