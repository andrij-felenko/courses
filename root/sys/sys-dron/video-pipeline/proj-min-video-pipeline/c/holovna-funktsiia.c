static gboolean once_start(gpointer u) { start_recording(u); return G_SOURCE_REMOVE; }
static gboolean once_stop (gpointer u) { stop_recording(u);  return G_SOURCE_REMOVE; }

int main(int argc, char **argv)
{
    gst_init(&argc, &argv);

    App a = { 0 };
    a.loop = g_main_loop_new(NULL, FALSE);

    if (!build_backbone(&a) || !add_view_branch(&a) || !add_rec_branch(&a)) {
        g_printerr("граф не зібрався\n");
        return 1;
    }

    GstBus *bus = gst_element_get_bus(a.pipeline);
    gst_bus_add_watch(bus, on_bus, &a);
    gst_object_unref(bus);

    gst_element_set_state(a.pipeline, GST_STATE_PLAYING);

    g_timeout_add_seconds( 5, once_start, &a);   /* демонстрація: пишемо з 5-ї */
    g_timeout_add_seconds(20, once_stop,  &a);   /* ... до 20-ї секунди */

    g_main_loop_run(a.loop);

    gst_element_set_state(a.pipeline, GST_STATE_NULL);
    gst_object_unref(a.pipeline);                /* єдиний unref, потрібний тут */
    g_main_loop_unref(a.loop);
    return 0;
}
