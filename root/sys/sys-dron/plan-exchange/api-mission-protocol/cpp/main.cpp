// Vehicle.cc — спершу команда, і лише як запасний варіант старе повідомлення
void Vehicle::setCurrentMissionSequence(int seq)
{
    if (!_firmwarePlugin->sendHomePositionToVehicle()) {
        seq--;                       // нумерація без домашнього пункту
    }
    sendMavCommandWithLambdaFallback(
        [this, seq]() { /* mavlink_msg_mission_set_current_pack_chan(…, seq) */ },
        defaultComponentId(),
        MAV_CMD_DO_SET_MISSION_CURRENT,
        true,                        // показати помилку
        static_cast<uint16_t>(seq));
}
