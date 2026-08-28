struct Entry {
    std::string method, url;
    Fields      headers;                   // заголовки збереженої відповіді
    Body        body;                      // тіло, спільне за підрахунком посилань
    std::vector<std::pair<std::string, std::string>> selecting;   // значення за Vary

    Wall::time_point   date_value{};       // Date, як його дав origin
    Wall::time_point   response_time_wall; // наш СТІННИЙ час у мить отримання
    Steady::time_point response_time_mono; // наш МОНОТОННИЙ час у ту саму мить
    Secs               response_delay{0};  // response_time − request_time
    Secs               age_value{0};       // Age, як його прислали
    CacheControl       cc;                 // розібраний Cache-Control відповіді
    int                status = 200;
};

// RFC 9111 §4.2.3
Secs current_age(const Entry& e, Steady::time_point now) {
    using std::chrono::duration_cast;
    const Secs apparent = std::max(Secs(0),
        duration_cast<Secs>(e.response_time_wall - e.date_value));
    const Secs corrected_age_value = e.age_value + e.response_delay;
    const Secs corrected_initial   = std::max(apparent, corrected_age_value);
    const Secs resident            = duration_cast<Secs>(now - e.response_time_mono);
    return corrected_initial + resident;
}
