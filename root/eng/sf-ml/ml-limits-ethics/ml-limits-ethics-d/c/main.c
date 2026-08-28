#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_FEATURES_DIM 16U

typedef struct {
    uint64_t timestamp_us;
    uint32_t model_hash_crc32;
    uint32_t operator_id;
    uint16_t action_code;
    float confidence_score;
    float threshold_used;
    float input_features[MAX_FEATURES_DIM];
    uint32_t record_checksum;
} DecisionAuditRecord;

static uint32_t compute_record_crc(const DecisionAuditRecord *rec) {
    uint32_t crc = 0xFFFFFFFFU;
    const uint8_t *bytes = (const uint8_t *)rec;
    size_t len = sizeof(DecisionAuditRecord) - sizeof(rec->record_checksum);
    for (size_t i = 0; i < len; ++i) {
        crc ^= bytes[i];
        for (int b = 0; b < 8; ++b) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(int32_t)(crc & 1U)));
        }
    }
    return ~crc;
}

bool audit_log_capture(
    DecisionAuditRecord *out_rec,
    uint64_t now_us,
    uint32_t model_hash,
    uint32_t op_id,
    uint16_t action,
    float conf,
    float thr,
    const float *features,
    size_t feat_count
) {
    if (!out_rec || !features || feat_count > MAX_FEATURES_DIM) {
        return false;
    }

    memset(out_rec, 0, sizeof(DecisionAuditRecord));
    out_rec->timestamp_us = now_us;
    out_rec->model_hash_crc32 = model_hash;
    out_rec->operator_id = op_id;
    out_rec->action_code = action;
    out_rec->confidence_score = conf;
    out_rec->threshold_used = thr;
    memcpy(out_rec->input_features, features, feat_count * sizeof(float));

    out_rec->record_checksum = compute_record_crc(out_rec);
    return true;
}
