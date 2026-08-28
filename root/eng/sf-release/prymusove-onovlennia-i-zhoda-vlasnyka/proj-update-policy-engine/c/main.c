#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>

#define INTERLOCK_SPEED_ZERO     (1U << 0)
#define INTERLOCK_BRAKE_ENGAGED  (1U << 1)
#define INTERLOCK_BATTERY_OK     (1U << 2)
#define INTERLOCK_ACTUATORS_OFF  (1U << 3)
#define INTERLOCK_FS_DRAINED     (1U << 4)

#define DEFAULT_REQUIRED_INTERLOCKS (INTERLOCK_SPEED_ZERO | \
                                    INTERLOCK_BRAKE_ENGAGED | \
                                    INTERLOCK_BATTERY_OK | \
                                    INTERLOCK_ACTUATORS_OFF | \
                                    INTERLOCK_FS_DRAINED)

typedef enum {
    URGENCY_STANDARD = 0,
    URGENCY_IMPORTANT = 1,
    URGENCY_MANDATORY = 2,
    URGENCY_CRITICAL_ZERO_DAY = 3,
    URGENCY_EMERGENCY_RECALL = 4
} update_urgency_level_t;

typedef enum {
    ENGINE_STATE_IDLE,
    ENGINE_STATE_LOADED,
    ENGINE_STATE_DEFERRED,
    ENGINE_STATE_WARNING,
    ENGINE_STATE_FORCE_PENDING,
    ENGINE_STATE_SAFETY_HOLD,
    ENGINE_STATE_READY_TO_ACTIVATE
} engine_state_t;

typedef struct {
    char bundle_id[64];
    update_urgency_level_t urgency;
    int64_t issued_at_epoch;
    int64_t hard_deadline_epoch;
    uint32_t max_deferrals;
    uint32_t deferral_step_sec;
    uint32_t required_interlocks_mask;
    uint32_t stability_hold_sec;
    uint32_t safety_wait_timeout_sec;
} update_policy_manifest_t;

typedef struct {
    uint32_t deferrals_used;
    int64_t next_prompt_epoch;
    int64_t hard_deadline_epoch;
    bool force_active;
} persistent_deferral_state_t;

typedef struct {
    double velocity_mps;
    bool parking_brake;
    uint8_t battery_soc_percent;
    bool is_ac_connected;
    double actuator_current_amps;
    bool filesystem_drained;
} raw_sensor_telemetry_t;

typedef struct {
    engine_state_t state;
    update_policy_manifest_t manifest;
    persistent_deferral_state_t persist;
    char state_file_path[256];
    struct timespec safe_conditions_start_mono;
    bool has_safe_start_time;
    int64_t safety_wait_start_epoch;
} update_policy_engine_t;

static int64_t get_current_epoch_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (int64_t)ts.tv_sec;
}

static struct timespec get_current_mono_time(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts;
}

static double timespec_diff_sec(const struct timespec* end, const struct timespec* start) {
    double sec = (double)(end->tv_sec - start->tv_sec);
    double nsec = (double)(end->tv_nsec - start->tv_nsec) / 1e9;
    return sec + nsec;
}

static bool save_persistent_state(const char* filepath, const persistent_deferral_state_t* state) {
    char temp_path[300];
    snprintf(temp_path, sizeof(temp_path), "%s.tmp", filepath);

    int fd = open(temp_path, O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (fd < 0) {
        return false;
    }

    ssize_t bytes_written = write(fd, state, sizeof(*state));
    if (bytes_written != (ssize_t)sizeof(*state)) {
        close(fd);
        unlink(temp_path);
        return false;
    }

    if (fsync(fd) != 0) {
        close(fd);
        unlink(temp_path);
        return false;
    }

    close(fd);
    return (rename(temp_path, filepath) == 0);
}

static bool load_persistent_state(const char* filepath, persistent_deferral_state_t* state) {
    int fd = open(filepath, O_RDONLY);
    if (fd < 0) {
        return false;
    }

    ssize_t bytes_read = read(fd, state, sizeof(*state));
    close(fd);
    return (bytes_read == (ssize_t)sizeof(*state));
}

static uint32_t sample_interlock_mask(const raw_sensor_telemetry_t* telem) {
    uint32_t mask = 0;
    if (telem->velocity_mps >= -0.01 && telem->velocity_mps <= 0.01) {
        mask |= INTERLOCK_SPEED_ZERO;
    }
    if (telem->parking_brake) {
        mask |= INTERLOCK_BRAKE_ENGAGED;
    }
    if (telem->battery_soc_percent >= 50 || telem->is_ac_connected) {
        mask |= INTERLOCK_BATTERY_OK;
    }
    if (telem->actuator_current_amps >= -0.05 && telem->actuator_current_amps <= 0.05) {
        mask |= INTERLOCK_ACTUATORS_OFF;
    }
    if (telem->filesystem_drained) {
        mask |= INTERLOCK_FS_DRAINED;
    }
    return mask;
}

void policy_engine_init(update_policy_engine_t* engine, const char* state_path) {
    memset(engine, 0, sizeof(*engine));
    engine->state = ENGINE_STATE_IDLE;
    strncpy(engine->state_file_path, state_path, sizeof(engine->state_file_path) - 1);
    engine->has_safe_start_time = false;
}

bool policy_engine_load_manifest(update_policy_engine_t* engine, const update_policy_manifest_t* manifest) {
    if (!engine || !manifest) return false;
    memcpy(&engine->manifest, manifest, sizeof(*manifest));

    if (!load_persistent_state(engine->state_file_path, &engine->persist)) {
        engine->persist.deferrals_used = 0;
        engine->persist.next_prompt_epoch = get_current_epoch_sec();
        engine->persist.hard_deadline_epoch = manifest->hard_deadline_epoch;
        engine->persist.force_active = false;
        save_persistent_state(engine->state_file_path, &engine->persist);
    }

    engine->state = ENGINE_STATE_LOADED;
    return true;
}

bool policy_engine_request_deferral(update_policy_engine_t* engine, uint32_t requested_sec) {
    if (!engine || engine->state == ENGINE_STATE_IDLE) return false;

    int64_t now = get_current_epoch_sec();
    if (now >= engine->manifest.hard_deadline_epoch ||
        engine->persist.deferrals_used >= engine->manifest.max_deferrals ||
        engine->manifest.urgency == URGENCY_EMERGENCY_RECALL) {
        return false;
    }

    uint32_t step = (requested_sec > 0) ? requested_sec : engine->manifest.deferral_step_sec;
    int64_t target_prompt = now + step;
    if (target_prompt > engine->manifest.hard_deadline_epoch) {
        target_prompt = engine->manifest.hard_deadline_epoch;
    }

    engine->persist.deferrals_used++;
    engine->persist.next_prompt_epoch = target_prompt;
    save_persistent_state(engine->state_file_path, &engine->persist);

    engine->state = ENGINE_STATE_DEFERRED;
    return true;
}

engine_state_t policy_engine_tick(update_policy_engine_t* engine, const raw_sensor_telemetry_t* telemetry) {
    if (!engine || engine->state == ENGINE_STATE_IDLE) return ENGINE_STATE_IDLE;

    int64_t now_epoch = get_current_epoch_sec();
    struct timespec now_mono = get_current_mono_time();

    bool deadline_reached = (now_epoch >= engine->manifest.hard_deadline_epoch);
    bool deferrals_out = (engine->persist.deferrals_used >= engine->manifest.max_deferrals);
    bool is_emergency = (engine->manifest.urgency == URGENCY_EMERGENCY_RECALL);

    if (deadline_reached || deferrals_out || is_emergency) {
        engine->persist.force_active = true;
    }

    int64_t total_window = engine->manifest.hard_deadline_epoch - engine->manifest.issued_at_epoch;
    int64_t elapsed_window = now_epoch - engine->manifest.issued_at_epoch;
    double progress = (total_window > 0) ? ((double)elapsed_window / (double)total_window) : 1.0;

    if (engine->persist.force_active) {
        engine->state = ENGINE_STATE_FORCE_PENDING;
    } else if (progress >= 0.80 || (engine->manifest.max_deferrals - engine->persist.deferrals_used <= 1)) {
        engine->state = ENGINE_STATE_WARNING;
    } else if (now_epoch < engine->persist.next_prompt_epoch) {
        engine->state = ENGINE_STATE_DEFERRED;
        return engine->state;
    } else {
        engine->state = ENGINE_STATE_LOADED;
    }

    uint32_t current_interlocks = sample_interlock_mask(telemetry);
    uint32_t req_mask = engine->manifest.required_interlocks_mask ? 
                        engine->manifest.required_interlocks_mask : DEFAULT_REQUIRED_INTERLOCKS;

    bool interlocks_passed = ((current_interlocks & req_mask) == req_mask);

    if (!interlocks_passed) {
        engine->has_safe_start_time = false;
        if (engine->persist.force_active) {
            if (engine->safety_wait_start_epoch == 0) {
                engine->safety_wait_start_epoch = now_epoch;
            }
            engine->state = ENGINE_STATE_SAFETY_HOLD;
        }
        return engine->state;
    }

    if (!engine->has_safe_start_time) {
        engine->safe_conditions_start_mono = now_mono;
        engine->has_safe_start_time = true;
        if (engine->persist.force_active) {
            engine->state = ENGINE_STATE_SAFETY_HOLD;
        }
        return engine->state;
    }

    double stable_duration = timespec_diff_sec(&now_mono, &engine->safe_conditions_start_mono);
    if (stable_duration >= (double)engine->manifest.stability_hold_sec) {
        if (engine->persist.force_active || engine->state == ENGINE_STATE_LOADED || engine->state == ENGINE_STATE_WARNING) {
            engine->state = ENGINE_STATE_READY_TO_ACTIVATE;
        }
    } else {
        if (engine->persist.force_active) {
            engine->state = ENGINE_STATE_SAFETY_HOLD;
        }
    }

    return engine->state;
}

int main(void) {
    printf("[C99 Engine Test Harness] Initializing Policy Evaluator...\n");
    const char* state_file = "/tmp/ota_test_policy.dat";
    unlink(state_file);

    update_policy_engine_t engine;
    policy_engine_init(&engine, state_file);

    int64_t now = get_current_epoch_sec();
    update_policy_manifest_t manifest = {
        .bundle_id = "com.fleet.firmware-amr-5.12.4",
        .urgency = URGENCY_CRITICAL_ZERO_DAY,
        .issued_at_epoch = now,
        .hard_deadline_epoch = now + 10,
        .max_deferrals = 2,
        .deferral_step_sec = 4,
        .required_interlocks_mask = DEFAULT_REQUIRED_INTERLOCKS,
        .stability_hold_sec = 2,
        .safety_wait_timeout_sec = 60
    };

    policy_engine_load_manifest(&engine, &manifest);

    raw_sensor_telemetry_t telem_moving = {
        .velocity_mps = 1.8,
        .parking_brake = false,
        .battery_soc_percent = 78,
        .is_ac_connected = false,
        .actuator_current_amps = 12.4,
        .filesystem_drained = false
    };

    printf("Step 1: Vehicle moving during advisory period -> Request Deferral 1...\n");
    policy_engine_tick(&engine, &telem_moving);
    bool d1 = policy_engine_request_deferral(&engine, 4);
    printf("Deferral 1 granted: %s (State: %d, used: %u)\n",
           d1 ? "YES" : "NO", engine.state, engine.persist.deferrals_used);

    printf("Step 2: Vehicle still moving, requesting Deferral 2...\n");
    bool d2 = policy_engine_request_deferral(&engine, 4);
    printf("Deferral 2 granted: %s (used: %u)\n", d2 ? "YES" : "NO", engine.persist.deferrals_used);

    printf("Step 3: Attempting Deferral 3 (exceeding limit of 2)...\n");
    bool d3 = policy_engine_request_deferral(&engine, 4);
    printf("Deferral 3 granted: %s (expected NO)\n", d3 ? "YES" : "NO");

    printf("Step 4: Simulating Hard Deadline arrival while robot is still moving...\n");
    engine.manifest.hard_deadline_epoch = get_current_epoch_sec() - 1;
    policy_engine_tick(&engine, &telem_moving);
    printf("Engine State: %d (expected SAFETY_HOLD=%d)\n", engine.state, ENGINE_STATE_SAFETY_HOLD);

    printf("Step 5: Robot parks safely; stabilizing interlocks for 2 seconds...\n");
    raw_sensor_telemetry_t telem_parked = {
        .velocity_mps = 0.0,
        .parking_brake = true,
        .battery_soc_percent = 77,
        .is_ac_connected = false,
        .actuator_current_amps = 0.0,
        .filesystem_drained = true
    };

    for (int i = 0; i < 3; ++i) {
        engine_state_t st = policy_engine_tick(&engine, &telem_parked);
        printf("Tick %d: State = %d\n", i + 1, st);
        sleep(1);
    }

    if (engine.state == ENGINE_STATE_READY_TO_ACTIVATE) {
        printf("[SUCCESS] Safe Window Granted: System authorized for A/B reboot!\n");
    } else {
        printf("[FAILURE] Engine did not transition to READY_TO_ACTIVATE\n");
    }

    unlink(state_file);
    return 0;
}
