// Обробка вхідного HEARTBEAT у C++: вилучення ідентифікатора та реєстрація апарата
void processIncomingHeartbeat(const mavlink_message_t& msg) {
    // Ігноруємо власні пакети станції
    if (msg.sysid == 255) return;

    mavlink_heartbeat_t hb;
    mavlink_msg_heartbeat_decode(&msg, &hb);

    uint8_t vehicle_sysid = msg.sysid;
    uint8_t vehicle_compid = msg.compid;
    bool is_armed = (hb.base_mode & MAV_MODE_FLAG_SAFETY_ARMED) != 0;

    std::cout << "[GCS] Виявлено апарат SysID: " << static_cast<int>(vehicle_sysid)
              << ", CompID: " << static_cast<int>(vehicle_compid)
              << ", Стек: " << (hb.autopilot == MAV_AUTOPILOT_ARDUPILOTMEGA ? "ArduPilot" : "PX4")
              << ", Стан моторів: " << (is_armed ? "ARMED" : "DISARMED") << "\n";
}
