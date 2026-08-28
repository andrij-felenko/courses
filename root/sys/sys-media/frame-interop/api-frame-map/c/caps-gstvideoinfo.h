void           gst_video_info_init          (GstVideoInfo *info);
gboolean       gst_video_info_from_caps     (GstVideoInfo *info, const GstCaps *caps);
GstCaps       *gst_video_info_to_caps       (const GstVideoInfo *info);
gboolean       gst_video_info_set_format    (GstVideoInfo *info, GstVideoFormat format,
                                             guint width, guint height);
GstVideoInfo  *gst_video_info_new           (void);                        /* 1.6  */
GstVideoInfo  *gst_video_info_new_from_caps (const GstCaps *caps);         /* 1.20 */
void           gst_video_info_free          (GstVideoInfo *info);          /* 1.6  */
gboolean       gst_video_info_align         (GstVideoInfo *info, GstVideoAlignment *align);
gboolean       gst_video_info_align_full    (GstVideoInfo *info, GstVideoAlignment *align,
                                             gsize plane_size[GST_VIDEO_MAX_PLANES]); /* 1.18 */
