typedef enum {
  GST_BUFFERING_STREAM,      /* нікуди не складаємо, лише невелика черга */
  GST_BUFFERING_DOWNLOAD,    /* качаємо у файл наперед */
  GST_BUFFERING_TIMESHIFT,   /* кільцевий буфер: можна відступити назад */
  GST_BUFFERING_LIVE         /* живий потік, наперед не забігти */
} GstBufferingMode;

GstQuery * gst_query_new_buffering         (GstFormat format);
void     gst_query_set_buffering_percent (GstQuery *q, gboolean busy, gint percent);
void     gst_query_set_buffering_stats   (GstQuery *q, GstBufferingMode mode,
                                          gint avg_in, gint avg_out, gint64 buffering_left);
void     gst_query_set_buffering_range   (GstQuery *q, GstFormat format,
                                          gint64 start, gint64 stop, gint64 estimated_total);
gboolean gst_query_add_buffering_range   (GstQuery *q, gint64 start, gint64 stop);
