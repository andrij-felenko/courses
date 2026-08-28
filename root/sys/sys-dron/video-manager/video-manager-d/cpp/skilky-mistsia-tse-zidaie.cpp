uint64_t total = 0;
for (const QFileInfo &video : std::as_const(vidList)) {
    total += video.size();
}

const uint64_t maxSize = SettingsManager::instance()->videoSettings()->maxVideoSize()->rawValue().toUInt() * qPow(1024, 2);
while ((total >= maxSize) && !vidList.isEmpty()) {
    const QFileInfo info = vidList.takeLast();
    total -= info.size();
    (void) QFile::remove(info.filePath());
}
