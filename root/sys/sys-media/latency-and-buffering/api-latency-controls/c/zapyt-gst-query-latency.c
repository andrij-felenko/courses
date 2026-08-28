GstQuery *q = gst_query_new_latency ();

if (gst_element_query (GST_ELEMENT (pipeline), q)) {
    gboolean     live;
    GstClockTime min, max;

    gst_query_parse_latency (q, &live, &min, &max);
    g_print ("live=%d  min=%" GST_TIME_FORMAT "  max=%" GST_TIME_FORMAT "\n",
             live, GST_TIME_ARGS (min), GST_TIME_ARGS (max));
}
gst_query_unref (q);
