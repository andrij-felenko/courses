template <typename T>
void validate_object(const T& obj) {
    template for (constexpr auto field : std::meta::nonstatic_data_members_of(^^T)) {
        if constexpr (std::meta::has_annotation<ValidationRule>(field)) {
            constexpr auto rule = *std::meta::get_annotation<ValidationRule>(field);
            auto val = obj.[: field :];
            if (val < rule.min_value || val > rule.max_value) {
                throw std::runtime_error("Валідація не пройдена");
            }
        }
    }
}
