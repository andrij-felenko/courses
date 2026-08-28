struct JsonKey {
    std::string_view name;
};

struct IgnoreInSerialization {};

struct UserProfile {
    [[=JsonKey{"user_identifier"}]]
    int id;

    [[=IgnoreInSerialization{}]]
    std::string internal_token;
};
