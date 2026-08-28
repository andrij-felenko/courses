class EventDispatcher {
public:
    void dispatch(const EventVariant& event_variant) const {
        std::visit(Overloaded{
            [](const PingEvent& ping) {
                std::cout << "[PING] Отримано пінг seq=" << ping.sequence_id
                          << " час=" << ping.timestamp << '\n';
            },
            [](const TelemetryEvent& telem) {
                std::cout << "[ТЕЛЕМЕТРІЯ] Напруга=" << telem.voltage
                          << " В, Струм=" << telem.current
                          << " А, Температура=" << telem.temperature << " °C\n";
            },
            [](const CommandEvent& cmd) {
                std::cout << "[КОМАНДА] Директива: \"" << cmd.command
                          << "\" (пріоритет=" << cmd.priority << ")\n";
            }
        }, event_variant);
    }
};
