GstVideoMeta *gst_buffer_get_video_meta      (GstBuffer *buffer);
GstVideoMeta *gst_buffer_get_video_meta_id   (GstBuffer *buffer, gint id);
GstVideoMeta *gst_buffer_add_video_meta      (GstBuffer *buffer, GstVideoFrameFlags flags,
                                              GstVideoFormat format, guint width, guint height);
GstVideoMeta *gst_buffer_add_video_meta_full (GstBuffer *buffer, GstVideoFrameFlags flags,
                                              GstVideoFormat format, guint width, guint height,
                                              guint n_planes,
                                              gsize offset[GST_VIDEO_MAX_PLANES],
                                              gint  stride[GST_VIDEO_MAX_PLANES]);

gboolean gst_video_meta_map              (GstVideoMeta *meta, guint plane, GstMapInfo *info,
                                          gpointer *data, gint *stride, GstMapFlags flags);
gboolean gst_video_meta_unmap            (GstVideoMeta *meta, guint plane, GstMapInfo *info);
gboolean gst_video_meta_set_alignment    (GstVideoMeta *meta, GstVideoAlignment alignment);   /* 1.18 */
gboolean gst_video_meta_get_plane_size   (GstVideoMeta *meta, gsize plane_size[GST_VIDEO_MAX_PLANES]);   /* 1.18 */
gboolean gst_video_meta_get_plane_height (GstVideoMeta *meta, guint plane_height[GST_VIDEO_MAX_PLANES]); /* 1.18 */
