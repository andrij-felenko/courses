void          cv::setNumThreads(int nthreads);   // 0 — послідовно; від'ємне — повернути типове
int           cv::getNumThreads();
int           cv::getNumberOfCPUs();
void          cv::setUseOptimized(bool onoff);
bool          cv::useOptimized();
bool          cv::checkHardwareSupport(int feature);
cv::String    cv::getHardwareFeatureName(int feature);
const cv::String& cv::getBuildInformation();
cv::String    cv::getVersionString();

bool       cv::ipp::useIPP();
void       cv::ipp::setUseIPP(bool flag);
cv::String cv::ipp::getIppVersion();
bool       cv::ipp::useIPP_NotExact();
void       cv::ipp::setUseIPP_NotExact(bool flag);
