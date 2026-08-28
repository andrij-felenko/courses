double VideoManager::aspectRatio() const
{
    // Живий розмір декодованого кадру важить найбільше
    if (!_videoSize.isEmpty()) {
        return static_cast<double>(_videoSize.width()) / _videoSize.height();
    }
    for (VideoReceiver *receiver : _videoReceivers) {          // далі — метадані камери
        QGCVideoStreamInfo *pInfo = receiver->videoStreamInfo();
        if (!receiver->isThermal() && pInfo && !pInfo->isThermal()) {
            return pInfo->aspectRatio();
        }
    }
    return _videoSettings->aspectRatio()->rawValue().toDouble();   // і аж потім налаштування
}
