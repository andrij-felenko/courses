static bool blur_region_nv12 (const GstVideoInfo *info, GstBuffer *buf, cv::Rect r)
{
  MappedFrame f (info, buf, GST_MAP_READWRITE);
  if (!f)
    return false;

  const int w = f.width (), h = f.height ();

  cv::Mat y  = f.plane (0, h,     w,     CV_8UC1);   /* яскравість */
  cv::Mat uv = f.plane (1, h / 2, w / 2, CV_8UC2);   /* U та V поруч */

  /* Межі ділянки мусять бути парними: одна пара U,V накриває квадрат 2×2,
     тож непарний край просто нікуди покласти. */
  r &= cv::Rect (0, 0, w, h);
  r = cv::Rect (r.x & ~1, r.y & ~1, r.width & ~1, r.height & ~1);
  if (r.width < 8 || r.height < 8)
    return true;

  cv::Rect ruv (r.x / 2, r.y / 2, r.width / 2, r.height / 2);

  cv::Mat yr = y (r), uvr = uv (ruv);                /* два види, обидва в кадрі */
  cv::GaussianBlur (yr,  yr,  cv::Size (0, 0), 9);
  cv::GaussianBlur (uvr, uvr, cv::Size (0, 0), 4.5);
  return true;
}
