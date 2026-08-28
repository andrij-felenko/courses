void Downloader::onTick(Ms now)
{
    now_ = now;
    if (state_ != State::Running) return;

    const Ms wait = std::min<Ms>(kIdle * (retries_ + 1), kIdleMax);
    if (now_ - lastData_ < wait) return;                        // черга ще йде

    if (retries_ >= kRetryCap) {                                // канал мовчить остаточно
        finish(goodPrefix(), State::Failed);
        return;
    }
    ++retries_;
    ++stat_.repeats;
    requestGap();
}
