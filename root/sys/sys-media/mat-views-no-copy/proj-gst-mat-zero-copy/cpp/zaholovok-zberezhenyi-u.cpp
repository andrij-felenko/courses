class MotionDetector {
  cv::Mat prev_;
public:
  void feed (const cv::Mat &frame)
  {
    if (!prev_.empty ()) {
      cv::Mat diff;
      cv::absdiff (prev_, frame, diff);
      report (cv::mean (diff)[0]);          /* середня зміна на піксель */
    }
    prev_ = frame;              /* ✗ копіює ЗАГОЛОВОК, не пікселі */
  //prev_ = frame.clone ();     /* ✓ власний блок із лічильником   */
  }
};
