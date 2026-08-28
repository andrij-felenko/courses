namespace physics::thermal {

class Psychrometrics {
public:
    [[nodiscard]] static std::optional<PsychroResult> compute(
        double temp_c,
        double rh_pct
    ) noexcept;
};

} // namespace physics::thermal
