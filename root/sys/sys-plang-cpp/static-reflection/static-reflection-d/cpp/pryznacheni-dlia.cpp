struct ValidationRule {
    int min_value;
    int max_value;
};

struct SerializedName {
    std::string_view key;
};

struct RegistrationForm {
    [[=SerializedName{"user_login"}]]
    std::string login;

    [[=ValidationRule{18, 120}]]
    int age;
};
