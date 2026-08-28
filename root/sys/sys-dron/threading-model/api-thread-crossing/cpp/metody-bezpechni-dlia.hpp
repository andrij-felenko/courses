// src/Comms/LinkInterface.h
void writeBytesThreadSafe(const char *bytes, int length);
void sendMessageThreadSafe(mavlink_message_t &message);

// src/Vehicle/Vehicle.h
bool sendMessageOnLinkThreadSafe(LinkInterface *link, mavlink_message_t message);
void sendJoystickDataThreadSafe(float roll, float pitch, float yaw, float thrust,
                                quint16 buttons, quint16 buttons2,
                                float pitchExtension, float rollExtension,
                                float aux1, float aux2, float aux3,
                                float aux4, float aux5, float aux6);
void sendJoystickAuxRcOverrideThreadSafe(
        const std::array<uint16_t, kAuxRcOverrideChannelCount> &channelValues,
        const std::array<bool, kAuxRcOverrideChannelCount> &channelEnabled,
        bool useRcOverride);
