// Ціле в PARAM_VALUE лежить БАЙТАМИ у полі float: борт кладе його memcpy,
// клієнт мусить прочитати дзеркально.
static int32_t paramToInt(const mavlink_param_value_t &pv)
{
    if (pv.param_type == MAV_PARAM_TYPE_REAL32) {
        return static_cast<int32_t>(std::lround(pv.param_value));
    }
    int32_t v = 0;
    std::memcpy(&v, &pv.param_value, sizeof v);
    return v;
}

static std::string paramName(const char id[16])
{
    char buf[17] = {};
    std::memcpy(buf, id, 16);        // поле фіксованої довжини, нуля може не бути
    return buf;
}

static void requestParam(Link &link, const std::string &name)
{
    char id[16] = {};
    std::memcpy(id, name.data(), std::min(name.size(), sizeof id));
    mavlink_message_t msg;
    mavlink_msg_param_request_read_pack(GCS_SYSID, GCS_COMPID, &msg,
                                        link.targetSystem(), MAV_COMP_ID_AUTOPILOT1,
                                        id, -1);     // −1 — шукати за іменем, не за індексом
    link.send(msg);
}

// Перелік каналів наперед невідомий: питаємо всі можливі, лишаємо ті, що відповіли.
static std::map<std::string, int> readOutputFunctions(Link &link, int maxChannels = 16)
{
    std::vector<std::string> wanted;
    for (const char *bank : {"PWM_MAIN_FUNC", "PWM_AUX_FUNC"}) {
        for (int ch = 1; ch <= maxChannels; ++ch) {
            wanted.push_back(std::string(bank) + std::to_string(ch));
        }
    }

    std::map<std::string, int> got;
    for (int round = 0; round < 2 && got.size() < wanted.size(); ++round) {
        for (const std::string &name : wanted) {
            if (!got.count(name)) requestParam(link, name);
        }
        const int64_t deadline = nowMs() + 1500;
        mavlink_message_t msg;
        while (nowMs() < deadline && got.size() < wanted.size()) {
            if (!link.recv(msg, 100) || msg.msgid != MAVLINK_MSG_ID_PARAM_VALUE) continue;
            mavlink_param_value_t pv;
            mavlink_msg_param_value_decode(&msg, &pv);
            const std::string name = paramName(pv.param_id);
            if (std::find(wanted.begin(), wanted.end(), name) != wanted.end()) {
                got[name] = paramToInt(pv);
            }
        }
    }
    return got;                                       // мовчазні імена просто не існують
}
