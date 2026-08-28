void Downloader::shrinkTo(uint64_t realEnd)
{
    if (realEnd >= size_) return;                    // оголошений розмір не збільшуємо
    size_ = realEnd;
    if (window_ * kWindow >= size_) return;
    bins_ = binsIn(window_);                         // хвостове вікно стало коротшим
    if (reqStart_ > bins_) reqStart_ = bins_;
    if (reqEnd_   > bins_) reqEnd_   = bins_;
    pending_ = table_.countZeros(reqStart_, reqEnd_);
}
