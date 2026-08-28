bool TlogReader::seekToByte(int64_t byteOffset) {
    const int64_t rec = resyncFrom(byteOffset);
    if (rec < 0 || !positionAtRecord(rec)) return false;

    std::vector<uint8_t> probe;
    uint64_t t = 0;
    if (!next(t, probe)) return false;            // перший кадр після зсуву
    bool confirmed = !_hasPending;                // це був останній запис у файлі
    if (!confirmed) confirmed = next(t, probe);   // за ним розібрався ще один
    if (!confirmed) return false;

    return positionAtRecord(rec);
}
