static const QString filter(QStringLiteral("*.%1").arg(_logFileExtension));
const QFileInfoList fileInfoList = tempDir.entryInfoList(filterList, QDir::Files);

for (const QFileInfo& fileInfo : fileInfoList) {
    if (fileInfo.size() == 0) {
        (void)QFile::remove(fileInfo.filePath());
        continue;
    }
    _saveTelemetryLog(fileInfo.filePath());
}
