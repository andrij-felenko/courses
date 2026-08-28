namespace physics::thermal {

class AntiCondensationController {
public:
    explicit AntiCondensationController(double margin_on_c = 2.0, double margin_off_c = 4.0);
    bool update(double surface_temp_c, double dew_point_c) noexcept;
    [[nodiscard]] bool is_heater_active() const noexcept;
private:
    double margin_on_;
    double margin_off_;
    bool heater_state_;
};

} // namespace physics::thermal
