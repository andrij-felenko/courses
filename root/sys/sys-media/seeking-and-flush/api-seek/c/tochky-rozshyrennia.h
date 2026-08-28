struct _GstBaseSrcClass {
  /* ... */
  gboolean      (*is_seekable)          (GstBaseSrc *src);
  gboolean      (*prepare_seek_segment) (GstBaseSrc *src, GstEvent *seek,
                                         GstSegment *segment);
  gboolean      (*do_seek)              (GstBaseSrc *src, GstSegment *segment);
  gboolean      (*get_size)             (GstBaseSrc *src, guint64 *size);
  gboolean      (*query)                (GstBaseSrc *src, GstQuery *query);
  gboolean      (*event)                (GstBaseSrc *src, GstEvent *event);
  gboolean      (*unlock)               (GstBaseSrc *src);
  gboolean      (*unlock_stop)          (GstBaseSrc *src);
  GstFlowReturn (*create)               (GstBaseSrc *src, guint64 offset,
                                         guint size, GstBuffer **buf);
};
