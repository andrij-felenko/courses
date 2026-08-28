void SokilFirmwarePlugin::initializeVehicle(Vehicle *vehicle)
{
    if (vehicle->isOfflineEditingVehicle()) {
        return;                                 // апарата немає — просити нема кого
    }

    auto *data = qobject_cast<SokilFirmwarePluginInstanceData*>(vehicle->firmwarePluginInstanceData());
    if (!data) {
        data = new SokilFirmwarePluginInstanceData(vehicle);
        vehicle->setFirmwarePluginInstanceData(data);   // Vehicle бере об'єкт собі в діти
    }
    data->lastStreamRequestTime = QTime::currentTime();

    struct StreamRequest { uint32_t msgId; int hz; };
    static constexpr StreamRequest rgRequests[] = {
        { MAVLINK_MSG_ID_ATTITUDE,              10 },   // горизонт має бути плавним
        { MAVLINK_MSG_ID_GLOBAL_POSITION_INT,    5 },   // мітка на мапі
        { MAVLINK_MSG_ID_VFR_HUD,                5 },
        { MAVLINK_MSG_ID_SYS_STATUS,             2 },   // батарея, датчики
        { MAVLINK_MSG_ID_GPS_RAW_INT,            2 },
        { MAVLINK_MSG_ID_HOME_POSITION,          1 },
        { MAVLINK_MSG_ID_EXTENDED_SYS_STATE,     1 },   // без нього не працює переривання посадки
    };

    for (const StreamRequest &request : rgRequests) {
        vehicle->sendMavCommand(vehicle->defaultComponentId(),
                                MAV_CMD_SET_MESSAGE_INTERVAL,
                                false,                                     // мовчки: старі збірки команди не знають
                                static_cast<float>(request.msgId),
                                static_cast<float>(1000000 / request.hz)); // інтервал у мікросекундах
    }
}
