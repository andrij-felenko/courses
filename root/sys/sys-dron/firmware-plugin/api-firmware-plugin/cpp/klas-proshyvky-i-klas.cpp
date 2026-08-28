// src/MAVLink/QGCMAVLinkTypes.h
struct QGCMAVLinkTypes {
    typedef int FirmwareClass_t;
    typedef int VehicleClass_t;
    static constexpr VehicleClass_t VehicleClassGeneric = 0;   // = MAV_TYPE_GENERIC
    static constexpr uint8_t maxRcChannels = 18;
};

// src/MAVLink/QGCMAVLink.h
class QGCMAVLink : public QObject, public QGCMAVLinkTypes { … };
