/* Небезпечний витік внутрішнього стану */
class LeakyConfig {
public:
    std::string& get_database_url() {
        std::lock_guard<std::mutex> guard(mutex_);
        return db_url_; // Повернення посилання в обхід м'ютекса!
    }
private:
    std::mutex mutex_;
    std::string db_url_;
};
