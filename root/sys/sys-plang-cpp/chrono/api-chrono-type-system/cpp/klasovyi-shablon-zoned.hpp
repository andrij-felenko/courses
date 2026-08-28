template <class Duration, class TimeZonePtr = const std::chrono::time_zone*>
class zoned_time {
public:
    zoned_time();
    zoned_time(TimeZonePtr z);
    zoned_time(std::string_view name);
    zoned_time(TimeZonePtr z, const sys_time<Duration>& st);
    zoned_time(std::string_view name, const sys_time<Duration>& st);

    // Методи доступу
    sys_time<Duration> get_sys_time() const;
    local_time<Duration> get_local_time() const;
    TimeZonePtr get_time_zone() const;
    sys_info get_info() const;
};
