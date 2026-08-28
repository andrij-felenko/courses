namespace std::chrono {
    // Повертає посилання на поточну базу даних TZDB
    const tzdb& get_tzdb();

    // Знаходить часовий пояс за його назвою в базі IANA (наприклад, "Europe/Kyiv")
    const time_zone* locate_zone(std::string_view tz_name);

    // Повертає поточний системний часовий пояс ОС
    const time_zone* current_zone();
}
