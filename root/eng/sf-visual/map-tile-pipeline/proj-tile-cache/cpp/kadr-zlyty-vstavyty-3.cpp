void TileRenderer::beginFrame(const Viewport& vp) {
    if (vp.generation != lastGeneration_) {
        scheduler_.newGeneration(vp.generation);
        lastGeneration_ = vp.generation;
    }

    // 1. Забрати доспіле. У кеш кладемо ВСЕ: байти вже заплачено.
    drained_.clear();
    ready_.drain(drained_);
    for (Ready& r : drained_) {
        cache_.insert(r.id, r.raster);
        uploadQueue_.push_back(std::move(r));
    }
    // Черга на завантаження не має рости: викинуте з неї лишається в кеші
    // й підніметься наступного кадру, якщо ще буде потрібне.
    while (uploadQueue_.size() > kMaxUploadBacklog) uploadQueue_.pop_front();

    // 2. Скласти потребу кадру й замовити те, чого немає.
    need_.clear();
    for (const TileId& id : visibleTiles(vp)) {
        need_.insert(id);
        if (!cache_.find(id)) scheduler_.request(id, vp);
    }
    scheduler_.reclaimSlot();

    // 3. Підрізати кеш — один раз, тут, у відомій точці кадру.
    cache_.trim(vp);

    // 4. Квота завантажень текстур: і за штуками, і за часом.
    const auto deadline = frameStart_ + std::chrono::microseconds(kUploadBudgetUs);
    int uploaded = 0;
    while (!uploadQueue_.empty() && uploaded < kMaxUploadsPerFrame
           && std::chrono::steady_clock::now() < deadline) {
        Ready r = std::move(uploadQueue_.front());
        uploadQueue_.pop_front();
        if (!need_.count(r.id)) continue;    // поки летів, перестав бути потрібним
        uploadTexture(r.id, *r.raster);      // растр живий, поки живий shared_ptr
        ++uploaded;
    }
}
