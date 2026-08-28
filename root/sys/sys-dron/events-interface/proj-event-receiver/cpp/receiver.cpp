/* збірка:
     git clone https://github.com/mavlink/c_library_v2
     c++ -std=c++17 -O2 -Wall -I c_library_v2 receiver.cpp -o receiver   */

namespace {

struct Log { unsigned delivered{}, requests{}, lost{}; } g;

mavlink_message_t packEvent(uint8_t sysid, uint8_t compid,
                            uint16_t sequence, uint32_t boot_ms)
{
    mavlink_event_t ev{};
    ev.id                    = 0x01352ce4;      // будь-яка подія з метаданих
    ev.event_time_boot_ms    = boot_ms;
    ev.sequence              = sequence;
    ev.log_levels            = 0x62;            // зовнішній Critical, внутрішній Info
    ev.destination_system    = 0;               // широкомовно
    ev.destination_component = MAV_COMP_ID_ALL;

    mavlink_message_t msg;
    mavlink_msg_event_encode(sysid, compid, &msg, &ev);
    return msg;
}

mavlink_message_t packCurrent(uint8_t sysid, uint8_t compid,
                              uint16_t sequence, uint8_t flags)
{
    mavlink_current_event_sequence_t cur{};
    cur.sequence = sequence;
    cur.flags    = flags;

    mavlink_message_t msg;
    mavlink_msg_current_event_sequence_encode(sysid, compid, &msg, &cur);
    return msg;
}

mavlink_message_t packError(uint8_t sysid, uint8_t compid, uint16_t sequence,
                            uint16_t oldest, uint8_t our_sysid, uint8_t our_compid)
{
    mavlink_response_event_error_t err{};
    err.target_system             = our_sysid;
    err.target_component          = our_compid;
    err.sequence                  = sequence;
    err.sequence_oldest_available = oldest;
    err.reason                    = MAV_EVENT_ERROR_REASON_UNAVAILABLE;

    mavlink_message_t msg;
    mavlink_msg_response_event_error_encode(sysid, compid, &msg, &err);
    return msg;
}

}  // namespace

int main()
{
    constexpr uint8_t kOurSys = 255, kOurComp = MAV_COMP_ID_MISSIONPLANNER;
    constexpr uint8_t kSys    = 1,   kComp    = MAV_COMP_ID_AUTOPILOT1;

    EventReceiver::Callbacks cb;
    cb.send_request = [](const mavlink_request_event_t &req) {
        ++g.requests;
        printf("  запит %u\n", unsigned(req.first_sequence));
    };
    cb.timer   = [](int /*ms*/) {};                 // час у стенді рухає onTimeout() рукою
    cb.deliver = [](const mavlink_event_t &ev) {
        ++g.delivered;
        printf("  прийнято seq=%u\n", unsigned(ev.sequence));
    };
    cb.lost = [](int n) {
        g.lost += unsigned(n);
        printf("  втрачено безповоротно %d\n", n);
    };

    EventReceiver rx(cb, kOurSys, kOurComp, kSys, kComp);

    // 1–2. звичайний хід. Борт стартує з 65535 − 10, тож перша подія — 65526
    rx.processMessage(packEvent(kSys, kComp, 65526, 30100));
    rx.processMessage(packEvent(kSys, kComp, 65527, 30250));

    // 3. подія «наперед»: 65528 і 65529 не долетіли
    rx.processMessage(packEvent(kSys, kComp, 65530, 30800));

    // 4. широкомовний номер підтверджує, що борт уже на 65530
    rx.processMessage(packCurrent(kSys, kComp, 65530, 0));

    // 5–7. борт віддає пропущене; кожна прийнята подія одразу тягне наступну
    rx.processMessage(packEvent(kSys, kComp, 65528, 30500));
    rx.processMessage(packEvent(kSys, kComp, 65529, 30640));
    rx.processMessage(packEvent(kSys, kComp, 65530, 30800));

    // 8. лічильник підходить до межі
    rx.processMessage(packEvent(kSys, kComp, 65531, 31200));

    // 9. новий пропуск — цього разу такий, що переживе обертання
    rx.processMessage(packEvent(kSys, kComp, 65534, 41000));

    // 10. відповіді немає: спрацював таймер
    rx.onTimeout();

    // 11. борт: цього вже немає, найстаріше доступне — 2 (номер уже за нулем)
    rx.processMessage(packError(kSys, kComp, 65532, 2, kOurSys, kOurComp));

    // 12. продовжуємо з найстарішого доступного
    rx.processMessage(packEvent(kSys, kComp, 2, 44300));

    // 13. запізніла копія події 1 — тепер це дублікат
    rx.processMessage(packEvent(kSys, kComp, 1, 44100));

    // 14. борт перезавантажився, а повідомлення з прапорцем RESET ми проґавили
    rx.processMessage(packEvent(kSys, kComp, 65526, 1200));

    const auto st = rx.stats();
    printf("\nдоставлено      %u\n", g.delivered);
    printf("запитів         %u\n", g.requests);
    printf("дублікатів      %u\n", st.duplicates);
    printf("втрачено        %u\n", g.lost);
    printf("перезавантажень %u\n", st.reboots);
    return 0;
}
