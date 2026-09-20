typedef struct {
    DhInMemoryZoneRepository* repo;
    DhActuatorEventSpy* spy;
    DhArmSecurityZoneUseCase* use_case;
    DhArmSecurityZoneResult last_result;
} DhSecurityHarness;

void dh_harness_given_zone(DhSecurityHarness* h, const char* id, const char* pin, bool open) {
    DhSecurityZone z = { .has_open_sensors = open };
    strncpy(z.id, id, sizeof(z.id));
    strncpy(z.pin_code, pin, sizeof(z.pin_code));
    dh_repo_save(h->repo, &z);
}

void dh_harness_when_arm(DhSecurityHarness* h, const char* id, const char* pin) {
    DhArmSecurityZoneCommand cmd = { id, pin };
    h->use_case->execute(h->use_case->context, &cmd, &h->last_result);
}

bool dh_harness_then_status_is(const DhSecurityHarness* h, DhArmZoneStatus exp) {
    return h->last_result.status == exp;
}

bool dh_harness_then_has_event(const DhSecurityHarness* h, const char* evt) {
    for (int i = 0; i < h->spy->count; ++i) {
        if (strcmp(h->spy->events[i], evt) == 0) return true;
    }
    return false;
}
