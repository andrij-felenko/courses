// Перетворення низькорівневих помилок бази даних у бізнес-помилки
std::expected<UserData, DomainError> fetch_user(uint64_t user_id) {
    return db_query_user(user_id) // Повертає std::expected<UserData, DbError>
        .transform_error([](DbError db_err) -> DomainError {
            switch (db_err) {
                case DbError::RecordNotFound: return DomainError::UserNotFound;
                case DbError::ConnectionLost: return DomainError::ServiceUnavailable;
                default:                      return DomainError::InternalSystemError;
            }
        });
}
