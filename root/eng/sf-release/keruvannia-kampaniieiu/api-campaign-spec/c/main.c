#include <stdint.h>
#include <stdbool.h>

#define MAX_NAME_LEN 64
#define MAX_URL_LEN 256
#define MAX_SHA256_HEX 65
#define MAX_SIG_LEN 128
#define MAX_HW_REVS 8
#define MAX_WAVES 8

typedef enum {
    CAMPAIGN_STATUS_DRAFT = 0,
    CAMPAIGN_STATUS_SCHEDULED,
    CAMPAIGN_STATUS_IN_PROGRESS,
    CAMPAIGN_STATUS_SOAKING,
    CAMPAIGN_STATUS_PAUSED_STOP_THE_LINE,
    CAMPAIGN_STATUS_ABORTED,
    CAMPAIGN_STATUS_COMPLETED
} CampaignStatus;

typedef enum {
    BREACH_ACTION_PAUSE_AND_ALERT = 0,
    BREACH_ACTION_EMERGENCY_ROLLBACK,
    BREACH_ACTION_ABORT
} BreachAction;

typedef struct {
    char version[MAX_NAME_LEN];
    char artifact_url[MAX_URL_LEN];
    char sha256[MAX_SHA256_HEX];
    char signature[MAX_SIG_LEN];
    char min_source_version[MAX_NAME_LEN];
    char max_source_version[MAX_NAME_LEN];
    uint32_t security_patch_level;
} TargetPackageSpec;

typedef struct {
    char hw_revisions[MAX_HW_REVS][MAX_NAME_LEN];
    uint32_t hw_revisions_count;
    uint32_t min_battery_pct;
    bool require_external_power;
    uint64_t min_free_storage_bytes;
} EligibilitySpec;

typedef struct {
    uint32_t min_sample_size;
    uint32_t heartbeat_timeout_sec;
    uint32_t evaluation_window_sec;
    double max_failure_rate_pct;
    double max_rollback_rate_pct;
    double max_silence_rate_pct;
    BreachAction action_on_breach;
} StopTheLinePolicy;

typedef struct {
    char name[MAX_NAME_LEN];
    double target_percentage;
    uint32_t max_in_flight;
    uint32_t soak_duration_sec;
    uint8_t utc_hour_start;
    uint8_t utc_hour_end;
} WaveSpec;

typedef struct {
    char campaign_id[MAX_NAME_LEN];
    char title[MAX_NAME_LEN * 2];
    uint64_t created_at_unix;
    TargetPackageSpec package;
    EligibilitySpec eligibility;
    StopTheLinePolicy stop_policy;
    WaveSpec waves[MAX_WAVES];
    uint32_t waves_count;
    uint32_t global_max_in_flight;
    double token_bucket_rate;
    uint32_t lease_timeout_sec;
} FleetCampaignSpec;
