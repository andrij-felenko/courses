void Downloader::requestGap()
{
    if (state_ != State::Running) return;
    if (window_ * kWindow >= size_) { finish(size_, State::Done); return; }

    uint32_t start = table_.firstZero(0, bins_);
    if (start == bins_) {                          // у вікні жодної дірки
        ++window_;
        if (window_ * kWindow >= size_) { finish(size_, State::Done); return; }
        table_.clear();
        bins_ = binsIn(window_);
        reqStart_ = reqEnd_ = pending_ = 0;
        retries_ = 0;
        requestGap();                              // нове вікно просимо цілком
        return;
    }

    uint32_t end = table_.firstOne(start, bins_);
    for (;;) {                                     // зливаємо близькі дірки
        const uint32_t next = table_.firstZero(end, bins_);
        if (next >= bins_ || next - end > kMerge) break;
        end = table_.firstOne(next, bins_);
    }

    const uint64_t ofs = window_ * kWindow + uint64_t(start) * kChunk;
    uint64_t cnt = uint64_t(end - start) * kChunk;
    if (ofs + cnt > size_) cnt = size_ - ofs;      // не просимо за кінцем файлу

    reqStart_ = start;  reqEnd_ = end;
    pending_  = table_.countZeros(start, end);
    lastData_ = now_;                              // тишу рахуємо від моменту запиту
    ++stat_.requests;
    tx_.requestData(id_, uint32_t(ofs), uint32_t(cnt));
}
