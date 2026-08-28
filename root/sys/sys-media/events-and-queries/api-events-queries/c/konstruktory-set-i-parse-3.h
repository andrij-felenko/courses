GstQuery * gst_query_new_allocation   (GstCaps *caps, gboolean need_pool);
void     gst_query_parse_allocation (GstQuery *q, GstCaps **caps, gboolean *need_pool);
void     gst_query_add_allocation_pool  (GstQuery *q, GstBufferPool *pool,
                                         guint size, guint min_buffers, guint max_buffers);
void     gst_query_add_allocation_param (GstQuery *q, GstAllocator *allocator,
                                         const GstAllocationParams *params);
void     gst_query_add_allocation_meta  (GstQuery *q, GType api, const GstStructure *params);
gboolean gst_query_find_allocation_meta (GstQuery *q, GType api, guint *index);

typedef enum {
  GST_SCHEDULING_FLAG_SEEKABLE          = 1 << 0,
  GST_SCHEDULING_FLAG_SEQUENTIAL        = 1 << 1,
  GST_SCHEDULING_FLAG_BANDWIDTH_LIMITED = 1 << 2
} GstSchedulingFlags;

GstQuery * gst_query_new_scheduling (void);
void     gst_query_set_scheduling  (GstQuery *q, GstSchedulingFlags flags,
                                    gint minsize, gint maxsize, gint align);
void     gst_query_add_scheduling_mode (GstQuery *q, GstPadMode mode);
gboolean gst_query_has_scheduling_mode_with_flags (GstQuery *q, GstPadMode mode,
                                                   GstSchedulingFlags flags);
