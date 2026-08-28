/* Замазує прямокутник ПРЯМО в кадрі конвеєра. */
static bool blur_region (const GstVideoInfo *info, GstBuffer *buf, cv::Rect r)
{
  MappedFrame f (info, buf, GST_MAP_READWRITE);
  if (!f)
    return false;

  cv::Mat bgr = f.plane (0, f.height (), f.width (), CV_8UC3);  /* без копії */

  r &= cv::Rect (0, 0, bgr.cols, bgr.rows);        /* обрізати межами кадру */
  if (r.width < 8 || r.height < 8)
    return true;

  cv::Mat roi = bgr (r);                           /* вид у виді, теж без копії */
  cv::GaussianBlur (roi, roi, cv::Size (0, 0), 9); /* пише В КАДР */
  cv::rectangle (bgr, r, cv::Scalar (0, 255, 0), 2);

  return true;
}   /* roi і bgr гинуть раніше за f — unmap робиться останнім */
