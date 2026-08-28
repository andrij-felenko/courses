void CustomPlugin::sendBeaconMode(Vehicle *vehicle, uint8_t mode, float radius_m)
{
    WeakLinkInterfacePtr weakLink = vehicle->vehicleLinkManager()->primaryLink();
    if (weakLink.expired()) {
        return;
    }
    SharedLinkInterfacePtr sharedLink = weakLink.lock();

    mavlink_message_t message{};
    mavlink_msg_perimeter_beacon_cmd_pack_chan(
        MAVLinkProtocol::instance()->getSystemId(),   // хто шле: станція
        MAVLinkProtocol::getComponentId(),
        sharedLink->mavlinkChannel(),                 // слот стану кодувальника
        &message,
        vehicle->id(), vehicle->compId(),             // кому: target_system, target_component
        mode, radius_m);

    vehicle->sendMessageOnLinkThreadSafe(sharedLink.get(), message);
}
