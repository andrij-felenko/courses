enum class DbError { ConnectionLost, RecordNotFound, CorruptedData };
enum class ApiError { InternalServerError, NotFound, Unauthorized };

std::expected<Record, DbError> load_from_db(int id);

std::expected<Record, ApiError> get_user_record(int id) {
    return load_from_db(id).transform_error([](DbError e) -> ApiError {
        switch (e) {
            case DbError::RecordNotFound: return ApiError::NotFound;
            case DbError::ConnectionLost:
            case DbError::CorruptedData:  return ApiError::InternalServerError;
        }
        std::unreachable();
    });
}
