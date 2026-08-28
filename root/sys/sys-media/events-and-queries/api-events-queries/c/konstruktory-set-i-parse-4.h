GstQuery * gst_query_new_accept_caps        (GstCaps *caps);
void     gst_query_parse_accept_caps        (GstQuery *q, GstCaps **caps);
void     gst_query_set_accept_caps_result   (GstQuery *q, gboolean result);
void     gst_query_parse_accept_caps_result (GstQuery *q, gboolean *result);

GstQuery * gst_query_new_caps         (GstCaps *filter);   /* filter може бути NULL */
void     gst_query_parse_caps         (GstQuery *q, GstCaps **filter);
void     gst_query_set_caps_result    (GstQuery *q, GstCaps *caps);
void     gst_query_parse_caps_result  (GstQuery *q, GstCaps **caps);

GstQuery * gst_query_new_drain    (void);

GstQuery * gst_query_new_context        (const gchar *context_type);
gboolean gst_query_parse_context_type (GstQuery *q, const gchar **context_type);
void     gst_query_set_context        (GstQuery *q, GstContext *context);
void     gst_query_parse_context      (GstQuery *q, GstContext **context);

GstQuery * gst_query_new_bitrate     (void);
void     gst_query_set_bitrate       (GstQuery *q, guint nominal_bitrate);
GstQuery * gst_query_new_selectable  (void);
void     gst_query_set_selectable    (GstQuery *q, gboolean selectable);
