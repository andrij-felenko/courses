static GstPadProbeReturn
trace_signals (GstPad *pad, GstPadProbeInfo *info, gpointer user_data)
{
  if (GST_PAD_PROBE_INFO_TYPE (info) & GST_PAD_PROBE_TYPE_EVENT_BOTH) {
    GstEvent *e = GST_PAD_PROBE_INFO_EVENT (info);

    g_print ("подія %-14s seqnum=%u  %s%s\n",
             GST_EVENT_TYPE_NAME (e), GST_EVENT_SEQNUM (e),
             GST_EVENT_IS_SERIALIZED (e) ? "у черзі" : "позачергова",
             GST_EVENT_IS_STICKY (e) ? ", липка" : "");
    return GST_PAD_PROBE_OK;                 /* нічого не чіпаємо */
  }

  if (GST_PAD_PROBE_INFO_TYPE (info) & GST_PAD_PROBE_TYPE_QUERY_BOTH) {
    GstQuery *q = GST_PAD_PROBE_INFO_QUERY (info);

    if (GST_QUERY_TYPE (q) == GST_QUERY_LATENCY) {
      gst_query_set_latency (q, TRUE, 40 * GST_MSECOND, 200 * GST_MSECOND);
      return GST_PAD_PROBE_HANDLED;          /* відповідь уже в запиті → той, хто питав, дістане TRUE */
    }
    g_print ("запит %s\n", gst_query_type_get_name (GST_QUERY_TYPE (q)));
    return GST_PAD_PROBE_OK;
  }
  return GST_PAD_PROBE_OK;
}

/* установлення */
GstPad *sinkpad = gst_element_get_static_pad (sink, "sink");
gulong  id = gst_pad_add_probe (sinkpad,
                                GST_PAD_PROBE_TYPE_EVENT_BOTH |
                                GST_PAD_PROBE_TYPE_EVENT_FLUSH |
                                GST_PAD_PROBE_TYPE_QUERY_BOTH,
                                trace_signals, NULL, NULL);
gst_object_unref (sinkpad);
