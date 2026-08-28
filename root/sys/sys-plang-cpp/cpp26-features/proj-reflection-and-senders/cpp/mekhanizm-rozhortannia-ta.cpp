struct GeoLocation {
    double latitude;
    double longitude;
};

struct UserAccount {
    uint64_t id;
    std::string username;
    bool is_active;
    GeoLocation location;
    std::vector<std::string> roles;
};

void demonstrate_serialization() {
    UserAccount account{
        .id = 1048576,
        .username = "system_operator",
        .is_active = true,
        .location = {.latitude = 50.4501, .longitude = 30.5234},
        .roles = {"admin", "telemetry_viewer", "audit"}
    };

    std::string json_output = to_json(account);
    std::cout << json_output << std::endl;
}
