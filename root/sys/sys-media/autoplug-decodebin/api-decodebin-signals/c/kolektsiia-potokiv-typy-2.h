/* transfer full у вихідному аргументі — знімати посилання вам */
void      gst_message_parse_stream_collection      (GstMessage *message,
                                                    GstStreamCollection **collection);
void      gst_message_parse_streams_selected       (GstMessage *message,
                                                    GstStreamCollection **collection);
guint     gst_message_streams_selected_get_size    (GstMessage *message);
/* transfer full */
GstStream *gst_message_streams_selected_get_stream (GstMessage *message, guint idx);

/* streams — GList рядків-ідентифікаторів; подія копіює їх собі (з 1.10) */
GstEvent *gst_event_new_select_streams   (GList *streams);
void      gst_event_parse_select_streams (GstEvent *event, GList **streams);
