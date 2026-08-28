template <typename T>
auto generate_create_table() -> std::string {
    constexpr auto type_info = ^^T;
    constexpr auto members = std::meta::nonstatic_data_members_of(type_info);

    std::string sql = "CREATE TABLE ";
    sql += std::meta::name_of(type_info);
    sql += " (\n";

    bool first = true;
    template for (constexpr auto member : members) {
        if (!first) sql += ",\n";

        sql += "    ";
        sql += std::meta::name_of(member);
        sql += " ";

        constexpr auto field_type = std::meta::type_of(member);
        if constexpr (field_type == ^^int || field_type == ^^uint32_t) {
            sql += "INTEGER";
        } else if constexpr (field_type == ^^double || field_type == ^^float) {
            sql += "REAL";
        } else if constexpr (field_type == ^^std::string) {
            sql += "TEXT";
        } else if constexpr (field_type == ^^bool) {
            sql += "BOOLEAN";
        } else {
            sql += "BLOB";
        }

        first = false;
    }

    sql += "\n);";
    return sql;
}
