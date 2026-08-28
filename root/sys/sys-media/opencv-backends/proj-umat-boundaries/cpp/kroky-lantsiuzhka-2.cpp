static const char* kCurveSrc = R"CLC(
  ... текст ядра з попереднього блоку ...
)CLC";

static bool curveOnDevice(const cv::UMat& src, cv::UMat& dst)
{
    // Останній аргумент — ключ, під яким скомпільоване ядро ляже в дисковий кеш.
    // Змінили текст ядра — змініть і ключ, інакше ризикуєте дістати стару збірку.
    static const cv::ocl::ProgramSource prog("app", "curve", kCurveSrc, "curve-v1");

    cv::ocl::Kernel k("applyCurve", prog);
    if (k.empty())
        return false;                      // драйвер не зібрав — чесно кажемо про це

    dst.create(src.size(), src.type());
    k.args(cv::ocl::KernelArg::ReadOnlyNoSize(src),
           cv::ocl::KernelArg::WriteOnly(dst),
           cv::ocl::KernelArg::PtrReadOnly(g_curveU));

    size_t global[2] = { (size_t)src.cols, (size_t)src.rows };
    return k.run(2, global, nullptr, /*sync=*/false);
}
