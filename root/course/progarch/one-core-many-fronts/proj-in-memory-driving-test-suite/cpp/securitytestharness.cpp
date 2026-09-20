class SecurityTestHarness {
public:
    SecurityTestHarness(ArmSecurityZoneUseCase& uc, InMemorySecurityZoneRepository& r, ActuatorEventSpy& s)
        : uc_(uc), repo_(r), spy_(s) {}

    void given_zone(const std::string& id, const std::string& pin, bool open) {
        repo_.save({id, pin, open, false});
    }

    void when_arming(const std::string& id, const std::string& pin) {
        last_result_ = uc_.execute({id, pin});
    }

    bool then_status_is(ArmZoneStatus exp) const { return last_result_.status == exp; }

    bool then_has_event(const std::string& evt) const {
        for (const auto& e : spy_.emitted_events()) if (e == evt) return true;
        return false;
    }

private:
    ArmSecurityZoneUseCase& uc_;
    InMemorySecurityZoneRepository& repo_;
    ActuatorEventSpy& spy_;
    ArmSecurityZoneResult last_result_{};
};
