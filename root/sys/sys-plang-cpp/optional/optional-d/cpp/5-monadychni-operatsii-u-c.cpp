// Підхід C++17: виснажлива драбина з вкладених if
std::optional<User> user = find_user(user_id);
if (user) {
    std::optional<Config> config = load_config(*user);
    if (config) {
        std::optional<Session> session = start_session(*config);
        if (session) {
            session->run();
        }
    }
}
