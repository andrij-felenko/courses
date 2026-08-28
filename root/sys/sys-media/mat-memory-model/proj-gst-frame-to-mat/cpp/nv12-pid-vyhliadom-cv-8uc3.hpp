const int    h  = GST_VIDEO_INFO_HEIGHT(&ff.info);
const int    w  = GST_VIDEO_INFO_WIDTH(&ff.info);
const size_t sy = (size_t) GST_VIDEO_INFO_PLANE_STRIDE(&ff.info, 0);

// Обидві умови мусять справдитися, інакше суцільного заголовка не буде:
CV_Assert(sy == (size_t) GST_VIDEO_INFO_PLANE_STRIDE(&ff.info, 1));   // кроки рівні
CV_Assert(GST_VIDEO_INFO_PLANE_OFFSET(&ff.info, 1) == sy * (size_t) h); // площини стикаються

cv::Mat nv12(h + h / 2, w, CV_8UC1, mi.data, sy);      // Y, а під ним UV
cv::cvtColor(nv12, bgr, cv::COLOR_YUV2BGR_NV12);        // ось тут і буде копія
