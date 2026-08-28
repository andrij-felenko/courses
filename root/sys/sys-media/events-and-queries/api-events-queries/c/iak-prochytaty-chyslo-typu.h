const gchar *      gst_event_type_get_name  (GstEventType type);
GstEventTypeFlags  gst_event_type_get_flags (GstEventType type);

#define GST_EVENT_TYPE(event)        (GST_EVENT_CAST(event)->type)
#define GST_EVENT_TYPE_NAME(event)   (gst_event_type_get_name (GST_EVENT_TYPE (event)))
#define GST_EVENT_SEQNUM(event)      (GST_EVENT_CAST(event)->seqnum)

#define GST_EVENT_IS_UPSTREAM(ev)    !!(GST_EVENT_TYPE (ev) & GST_EVENT_TYPE_UPSTREAM)
#define GST_EVENT_IS_DOWNSTREAM(ev)  !!(GST_EVENT_TYPE (ev) & GST_EVENT_TYPE_DOWNSTREAM)
#define GST_EVENT_IS_SERIALIZED(ev)  !!(GST_EVENT_TYPE (ev) & GST_EVENT_TYPE_SERIALIZED)
#define GST_EVENT_IS_STICKY(ev)      !!(GST_EVENT_TYPE (ev) & GST_EVENT_TYPE_STICKY)
