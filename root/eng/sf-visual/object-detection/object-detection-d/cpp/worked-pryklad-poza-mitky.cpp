cv::Mat frame = grab_frame();
std::vector<int> ids;
std::vector<std::vector<cv::Point2f>> corners;

// 1. знайти мітки та їхні кути в кадрі
cv::aruco::detectMarkers(frame, dict, corners, ids);

if (!ids.empty()) {
    std::vector<cv::Vec3d> rvecs, tvecs;
    // 2. PnP для кожної мітки: розмір 0.15 м, відомі K (матриця) і dist
    cv::aruco::estimatePoseSingleMarkers(corners, 0.15f, K, dist, rvecs, tvecs);

    // 3. поворот rvec → матриця → кути Ейлера
    cv::Mat R;
    cv::Rodrigues(rvecs[0], R);                  // вектор повороту → матриця 3×3
    double yaw   = atan2(R.at<double>(1,0), R.at<double>(0,0));
    double pitch = atan2(-R.at<double>(2,0),
                         hypot(R.at<double>(2,1), R.at<double>(2,2)));
    double roll  = atan2(R.at<double>(2,1), R.at<double>(2,2));
    // tvecs[0] = (X, Y, Z) зсув мітки в метрах відносно камери
}
