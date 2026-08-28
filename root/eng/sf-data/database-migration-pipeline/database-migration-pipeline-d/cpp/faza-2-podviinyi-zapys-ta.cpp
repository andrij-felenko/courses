// Логіка оновлення профілю у версії коду v1.1 (Dual Write)
void update_user_phone(PgConnection& conn, int64_t user_id, std::string_view raw_phone) {
    std::string normalized_phone = format_e164(raw_phone);

    std::string query = std::format(
        "UPDATE users SET phone = '{}', phone_e164 = '{}', updated_at = NOW() WHERE id = {};",
        raw_phone, normalized_phone, user_id
    );
    PgResultPtr res(conn.exec(query));
}
