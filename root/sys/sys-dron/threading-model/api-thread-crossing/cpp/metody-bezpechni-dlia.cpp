void LinkInterface::writeBytesThreadSafe(const char *bytes, int length)
{
    const QByteArray data(bytes, length);
    (void) QMetaObject::invokeMethod(this, "_writeBytes", Qt::AutoConnection, data);
}

void LinkInterface::sendMessageThreadSafe(mavlink_message_t &message)
{
    if (_signingController) {
        (void) _signingController->signOutgoing(message);
    }

    uint8_t buffer[MAVLINK_MAX_PACKET_LEN];
    const int len = mavlink_msg_to_send_buffer(buffer, &message);
    writeBytesThreadSafe(reinterpret_cast<const char *>(buffer), len);
}
