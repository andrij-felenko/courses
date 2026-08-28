static bool ocl_localRange(cv::InputArray _src, cv::OutputArray _dst, int ksize,
                           cv::InputArray _mask, cv::OutputArray _hist)
{
    if (_hist.needed())
        return false;               // гістограму на пристрої ми не рахуємо — чесно віддаємо все

    static const cv::ocl::ProgramSource prog("cvx", "localRange",
                                             kLocalRangeSrc, "localRange-v1");

    const bool hasMask = !_mask.empty();
    const cv::String opts = cv::format("-D KSIZE=%d%s", ksize,
                                       hasMask ? " -D HAVE_MASK" : "");

    cv::ocl::Kernel k("localRange", prog, opts);
    if (k.empty())
        return false;               // ще НІЧОГО не змінено в приймачі — так і має бути

    cv::UMat src  = _src.getUMat();
    cv::UMat mask = hasMask ? _mask.getUMat() : cv::UMat();
    CV_Assert(!hasMask || mask.size() == src.size());

    _dst.create(src.size(), CV_8UC1);
    cv::UMat dst = _dst.getUMat();

    cv::UMat tmp, out = dst;
    if (dst.u == src.u) {           // in-place — те саме питання, що й на процесорі
        tmp.create(src.size(), CV_8UC1);
        out = tmp;
    }

    if (hasMask)
        k.args(cv::ocl::KernelArg::ReadOnlyNoSize(src),
               cv::ocl::KernelArg::WriteOnly(out),
               cv::ocl::KernelArg::ReadOnlyNoSize(mask));
    else
        k.args(cv::ocl::KernelArg::ReadOnlyNoSize(src),
               cv::ocl::KernelArg::WriteOnly(out));

    size_t global[2] = { (size_t)out.cols, (size_t)out.rows };
    if (!k.run(2, global, nullptr, /*sync=*/false))
        return false;

    if (!tmp.empty())
        tmp.copyTo(dst);
    return true;
}
