void MAVLinkProtocol::_forward(const mavlink_message_t& message)
{
    if (message.msgid == MAVLINK_MSG_ID_SETUP_SIGNING) {
        return;
    }
    if (!SettingsManager::instance()->mavlinkSettings()->forwardMavlink()->rawValue().toBool()) {
        return;
    }
    SharedLinkInterfacePtr forwardingLink = LinkManager::instance()->mavlinkForwardingLink();
    if (!forwardingLink) {
        return;
    }
    const QByteArray bytes = MAVLinkSigning::serializeUnsignedCopy(message);
    (void)forwardingLink->writeBytesThreadSafe(bytes.constData(), bytes.size());
}
