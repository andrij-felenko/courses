static void reportCompute()
{
    std::cout << "Паралелізм: " << buildInfoHead("Parallel framework")
              << ", потоків " << cv::getNumThreads()
              << " із " << cv::getNumberOfCPUs() << " процесорів\n";

    std::cout << "Вектори\n"
              << "  зібрано під: " << cv::getCPUFeaturesLine() << "\n"
              << "  процесор має:";
    for (int f : { CV_CPU_SSE4_2, CV_CPU_AVX, CV_CPU_AVX2,
                   CV_CPU_AVX512_SKX, CV_CPU_NEON })
        if (cv::checkHardwareSupport(f))
            std::cout << " " << cv::getHardwareFeatureName(f);
    std::cout << "\n";

    std::cout << "OpenCL: рантайм " << (cv::ocl::haveOpenCL() ? "є" : "немає")
              << ", T-API " << (cv::ocl::useOpenCL() ? "увімкнено" : "вимкнено")
              << "\n";
    if (!cv::ocl::haveOpenCL()) return;
    try {
        const cv::ocl::Device& dev = cv::ocl::Device::getDefault();
        if (!dev.empty())
            std::cout << "  " << dev.name() << " / " << dev.vendorName()
                      << " / " << dev.version()
                      << ", блоків " << dev.maxComputeUnits() << "\n";
    } catch (const cv::Exception& e) {
        std::cout << "  пристрій не піднявся: " << e.err << "\n";
    }
}
