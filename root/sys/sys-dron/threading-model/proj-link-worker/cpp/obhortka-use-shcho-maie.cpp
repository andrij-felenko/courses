void DemoLink::_onChunk(const Chunk &chunk)
{
    const qint64 residence = monoNs() - chunk.stampNs;

    _stats->delivered.fetch_add(1, std::memory_order_relaxed);
    _stats->residenceLastNs.store(residence, std::memory_order_relaxed);
    if (residence > _stats->residenceMaxNs.load(std::memory_order_relaxed))
        _stats->residenceMaxNs.store(residence, std::memory_order_relaxed);

    emit bytesReceived(chunk.bytes);
}
