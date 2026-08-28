/* пули */
void   gst_query_add_allocation_pool        (GstQuery *q, GstBufferPool *pool,
                                             guint size, guint min_buffers, guint max_buffers);
guint  gst_query_get_n_allocation_pools     (GstQuery *q);
void   gst_query_parse_nth_allocation_pool  (GstQuery *q, guint index, GstBufferPool **pool,
                                             guint *size, guint *min, guint *max);
void   gst_query_set_nth_allocation_pool    (GstQuery *q, guint index, GstBufferPool *pool,
                                             guint size, guint min, guint max);
void   gst_query_remove_nth_allocation_pool (GstQuery *q, guint index);

/* параметри виділення */
void   gst_query_add_allocation_param       (GstQuery *q, GstAllocator *allocator,
                                             const GstAllocationParams *params);
guint  gst_query_get_n_allocation_params    (GstQuery *q);
void   gst_query_parse_nth_allocation_param (GstQuery *q, guint index, GstAllocator **allocator,
                                             GstAllocationParams *params);

/* метадані */
void     gst_query_add_allocation_meta       (GstQuery *q, GType api, const GstStructure *params);
guint    gst_query_get_n_allocation_metas    (GstQuery *q);
GType    gst_query_parse_nth_allocation_meta (GstQuery *q, guint index,
                                              const GstStructure **params);
gboolean gst_query_find_allocation_meta      (GstQuery *q, GType api, guint *index);
