if (framing == MAVLINK_FRAMING_OK || framing == MAVLINK_FRAMING_BAD_SIGNATURE) {
    if (SigningController* const sigCtrl = link->signing()) {
        if (sigCtrl->processFrame(framing == MAVLINK_FRAMING_OK, message)) {
            resetSequenceTracking(link);
        }
    }
}
if (framing != MAVLINK_FRAMING_OK) {
    continue;
}
