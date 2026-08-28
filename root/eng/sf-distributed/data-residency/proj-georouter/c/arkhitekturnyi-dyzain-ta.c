#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#define MAX_JURISDICTIONS 8
#define MAX_REGIONS_PER_JURISDICTION 4
#define MAX_NAME_LEN 32
#define MAX_PAYLOAD_LEN 256
#define TOKEN_HEX_LEN 65

typedef enum {
    JURISDICTION_EU_EEA = 0,
    JURISDICTION_US_FED = 1,
    JURISDICTION_APAC   = 2,
    JURISDICTION_UNKNOWN = -1
} jurisdiction_id_t;

typedef enum {
    EGRESS_FORBIDDEN = 0,
    EGRESS_PERMITTED_PSEUDONYMIZED = 1,
    EGRESS_UNRESTRICTED = 2
} egress_policy_t;

typedef enum {
    ROUTER_OK = 0,
    ROUTER_ERR_JURISDICTION_UNKNOWN = 1,
    ROUTER_ERR_CROSS_BORDER_VIOLATION = 2,
    ROUTER_ERR_TOKENIZATION_FAILED = 3,
    ROUTER_ERR_BUFFER_OVERFLOW = 4
} router_status_t;

/* Опис конфігурації юрисдикції */
typedef struct {
    jurisdiction_id_t id;
    char name[MAX_NAME_LEN];
    char allowed_regions[MAX_REGIONS_PER_JURISDICTION][MAX_NAME_LEN];
    size_t region_count;
    egress_policy_t egress_policy;
    char hsm_key_salt[MAX_NAME_LEN];
} jurisdiction_config_t;

/* Вхідна транзакція клієнта */
typedef struct {
    char transaction_id[MAX_NAME_LEN];
    char country_code[4];       /* "DE", "FR", "US", "SG" */
    char tenant_id[MAX_NAME_LEN];
    char customer_name[MAX_NAME_LEN];
    char customer_iban[MAX_NAME_LEN];
    double amount;
    char target_datacenter[MAX_NAME_LEN];
} transaction_request_t;

/* Знеособлений вихідний пакет для глобальної аналітики */
typedef struct {
    char transaction_id[MAX_NAME_LEN];
    jurisdiction_id_t jurisdiction;
    char name_token[TOKEN_HEX_LEN];
    char iban_token[TOKEN_HEX_LEN];
    double amount;
    bool is_compliant;
} anonymized_event_t;
