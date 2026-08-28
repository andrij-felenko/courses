const QString source = _videoSettings->videoSource()->rawValue().toString();
if (source == VideoSettings::videoSourceUDPH264) {
    settingsChanged |= _updateVideoUri(receiver, QStringLiteral("udp://%1").arg(_videoSettings->udpUrl()->rawValue().toString()));
} else if (source == VideoSettings::videoSourceUDPH265) {
    settingsChanged |= _updateVideoUri(receiver, QStringLiteral("udp265://%1").arg(_videoSettings->udpUrl()->rawValue().toString()));
} else if (source == VideoSettings::videoSourceMPEGTS) {
    settingsChanged |= _updateVideoUri(receiver, QStringLiteral("mpegts://%1").arg(_videoSettings->udpUrl()->rawValue().toString()));
} else if (source == VideoSettings::videoSourceRTSP) {
    settingsChanged |= _updateVideoUri(receiver, _videoSettings->rtspUrl()->rawValue().toString());
}
