enum class HttpCode {
    Ok = 200,
    NotFound = 404,
    InternalError = 500
};

std::string_view get_status_message(HttpCode code) {
    switch (code) {
        using enum HttpCode; // Усі елементи HttpCode доступні без префікса
        case Ok:            return "200 OK";
        case NotFound:      return "404 Not Found";
        case InternalError: return "500 Internal Server Error";
    }
    return "Unknown";
}
