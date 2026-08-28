namespace app {

void on_valve_command(const embedded::mqtt::Message& msg, void* /*user_ctx*/) {
    if (msg.tokens.empty()) {
        return;
    }
    const auto valve_name = msg.tokens[0].value;
    const std::string_view payload_str(reinterpret_cast<const char*>(msg.payload.data()),
                                       msg.payload.size());

    if (valve_name == "valve01" && payload_str == "OPEN") {
        // Відкриття апаратного клапана
    }
}

void on_config_update(const embedded::mqtt::Message& msg, void* /*user_ctx*/) {
    // msg.tokens[0].value містить увесь підшлях конфігурації після '#'
}

void setup_router(embedded::mqtt::TopicRouter<16, 8>& router) {
    router.add_route("agro-corp/site-01/node-42/cmd/+", on_valve_command);
    router.add_route("agro-corp/site-01/node-42/config/#", on_config_update);
}

} // namespace app
