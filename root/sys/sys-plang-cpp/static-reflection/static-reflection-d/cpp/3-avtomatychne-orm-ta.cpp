template <typename T>
auto generate_ddl() -> std::string {
    std::string sql = std::format("CREATE TABLE {} (\n", std::meta::name_of(^^T));
    bool first = true;

    template for (constexpr auto field : std::meta::nonstatic_data_members_of(^^T)) {
        if (!first) sql += ",\n";
        constexpr auto ft = std::meta::type_of(field);
        std::string_view type_name = (ft == ^^int) ? "INTEGER" :
                                     (ft == ^^double) ? "REAL" : "TEXT";
        sql += std::format("    {} {}", std::meta::name_of(field), type_name);
        first = false;
    }

    sql += "\n);";
    return sql;
}
