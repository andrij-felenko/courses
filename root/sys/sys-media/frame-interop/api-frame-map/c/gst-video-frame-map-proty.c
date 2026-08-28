GstVideoInfo  info;
GstVideoFrame frame;

if (!gst_video_info_from_caps (&info, caps))
  return GST_FLOW_NOT_NEGOTIATED;

if (!gst_video_frame_map (&frame, &info, buffer, GST_MAP_READ))
  return GST_FLOW_ERROR;

/* … робота з GST_VIDEO_FRAME_PLANE_DATA / PLANE_STRIDE … */

gst_video_frame_unmap (&frame);        /* і на кожному ранньому виході теж */
