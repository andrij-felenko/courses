GstVideoFrame frame;

/* gst_video_frame_map читає GstVideoMeta, якщо вона є,
   інакше рахує розкладку з GstVideoInfo (щільне пакування) */
if (gst_video_frame_map (&frame, &vinfo, buf, GST_MAP_READ)) {
  const guint8 *y_plane = GST_VIDEO_FRAME_PLANE_DATA (&frame, 0);
  gint          y_stride = GST_VIDEO_FRAME_PLANE_STRIDE (&frame, 0);
  gint          height   = GST_VIDEO_FRAME_HEIGHT (&frame);

  for (gint row = 0; row < height; row++) {
    const guint8 *line = y_plane + (gsize) row * y_stride;   /* НЕ · width */
    /* … обробка рядка … */
  }
  gst_video_frame_unmap (&frame);
}
