void scaleAndMask(cv::InputArray _src, cv::OutputArray _dst,
                  cv::OutputArray _mask, double k)
{
    // 1. Заборонене відсіюємо явно — до першого дотику до пам'яті.
    CV_Assert(!_src.empty());
    CV_Assert(_src.kind() != cv::_InputArray::CUDA_GPU_MAT);

    // 2. Вхід беремо ДО create: вхід і вихід можуть виявитися тим самим об'єктом.
    cv::Mat src = _src.getMat();

    // 3. Виділяємо приймач. Розмір збігається — виклик нічого не робить.
    _dst.create(src.size(), src.type());
    cv::Mat dst = _dst.getMat();

    src.convertTo(dst, src.type(), k);

    // 4. Необов'язковий вихід — лише якщо його справді просили.
    if (_mask.needed())
    {
        _mask.create(src.size(), CV_8UC1);
        cv::Mat mask = _mask.getMat();
        cv::compare(dst, 0, mask, cv::CMP_GT);
    }
}
