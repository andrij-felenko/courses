void print(int);
void print(std::string_view);
void print(double, int);

consteval auto find_unary_int_overload(std::meta::info fn_name) -> std::meta::info {
    for (auto candidate : std::meta::overloads_of(fn_name)) {
        auto params = std::meta::parameters_of(candidate);
        if (params.size() == 1 && std::meta::type_of(params[0]) == ^^int) {
            return candidate;
        }
    }
    return ^^void;
}
