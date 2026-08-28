GstVideoFrame vf;
if (!gst_video_frame_map(&vf, &info, buffer, GST_MAP_READ))
    return;

cv::Mat view(GST_VIDEO_FRAME_HEIGHT(&vf),
             GST_VIDEO_FRAME_WIDTH(&vf),
             CV_8UC3,
             GST_VIDEO_FRAME_PLANE_DATA(&vf, 0),
             GST_VIDEO_FRAME_PLANE_STRIDE(&vf, 0));   // крок — від конвеєра!

detect(view);                    // читаємо на місці, не скопіювавши байта

gst_video_frame_unmap(&vf);      // відображення знято: view тепер висячий
