std::optional<User> user = find_user(id);
if (user) {
    std::optional<Config> config = load_config(*user);
    if (config) {
        std::optional<Server> server = connect_server(*config);
        if (server) {
            server->process();
        }
    }
}
