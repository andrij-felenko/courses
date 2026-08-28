// OpenCV 2.4: розгалуження живе НЕ в бібліотеці, а у вашому коді
cv::ocl::DevicesInfo devices;
if (cv::ocl::getOpenCLDevices(devices) > 0) {   // чи є тут узагалі пристрій
    cv::ocl::setDevice(devices[0]);
    cv::ocl::oclMat gsrc(src), gdst;            // конструктор = пересилання туди
    cv::ocl::resize(gsrc, gdst, dsize);
    gdst.download(dst);                         // і пересилання назад
} else {
    cv::resize(src, dst, dsize);                // те саме, іншим іменем
}
