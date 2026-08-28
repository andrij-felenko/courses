void PerimeterFactGroup::setMode(Vehicle *vehicle, int mode, double radiusM)
{
    if (!vehicle) {
        return;
    }

    SharedLinkInterfacePtr link = vehicle->vehicleLinkManager()->primaryLink().lock();
    if (!link) {
        qCWarning(CustomLog) << "Периметр: основного каналу немає";
        return;
    }

    mavlink_message_t message{};
    mavlink_msg_perimeter_beacon_cmd_pack_chan(
        MAVLinkProtocol::instance()->getSystemId(),   // хто шле: станція
        MAVLinkProtocol::getComponentId(),
        link->mavlinkChannel(),                       // слот стану кодувальника
        &message,
        vehicle->id(), vehicle->compId(),             // кому: target_system, target_component
        static_cast<uint8_t>(mode),
        static_cast<float>(radiusM));

    if (!vehicle->sendMessageOnLinkThreadSafe(link.get(), message)) {
        qCWarning(CustomLog) << "Периметр: канал зник між перевіркою й відправкою";
    }
}
