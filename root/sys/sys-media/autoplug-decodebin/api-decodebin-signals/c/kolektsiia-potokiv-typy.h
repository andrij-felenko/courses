guint         gst_stream_collection_get_size        (GstStreamCollection *collection);
/* transfer none — колекція лишається власником */
GstStream *   gst_stream_collection_get_stream      (GstStreamCollection *collection,
                                                     guint index);
const gchar * gst_stream_collection_get_upstream_id (GstStreamCollection *collection);

/* усе про один потік */
const gchar * gst_stream_get_stream_id    (GstStream *stream);   /* transfer none */
GstStreamType gst_stream_get_stream_type  (GstStream *stream);
GstCaps *     gst_stream_get_caps         (GstStream *stream);   /* transfer full */
GstTagList *  gst_stream_get_tags         (GstStream *stream);   /* transfer full */
GstStreamFlags gst_stream_get_stream_flags (GstStream *stream);

const gchar * gst_stream_type_get_name    (GstStreamType stype);
