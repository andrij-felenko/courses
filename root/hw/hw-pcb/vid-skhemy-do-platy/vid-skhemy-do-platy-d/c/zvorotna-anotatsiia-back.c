#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    ECO_NO_CHANGE,
    ECO_NET_CREATED,
    ECO_NET_DELETED,
    ECO_PINS_MODIFIED
} EcoStatus;

typedef struct EcoDiffResult {
    char net_name[64];
    EcoStatus status;
    int added_pins_count;
    int removed_pins_count;
} EcoDiffResult;

static int string_in_array(const char* target, const char* const* arr, int size) {
    for (int i = 0; i < size; ++i) {
        if (strcmp(target, arr[i]) == 0) return 1;
    }
    return 0;
}

EcoDiffResult compute_eco_diff(const char* net_name,
                               const char* const* old_pins, int old_count,
                               const char* const* new_pins, int new_count) {
    EcoDiffResult res;
    strncpy(res.net_name, net_name, 63);
    res.net_name[63] = '\0';
    res.added_pins_count = 0;
    res.removed_pins_count = 0;

    if (old_count == 0 && new_count > 0) {
        res.status = ECO_NET_CREATED;
        res.added_pins_count = new_count;
        return res;
    }
    if (old_count > 0 && new_count == 0) {
        res.status = ECO_NET_DELETED;
        res.removed_pins_count = old_count;
        return res;
    }

    for (int i = 0; i < new_count; ++i) {
        if (!string_in_array(new_pins[i], old_pins, old_count)) {
            res.added_pins_count++;
        }
    }
    for (int i = 0; i < old_count; ++i) {
        if (!string_in_array(old_pins[i], new_pins, new_count)) {
            res.removed_pins_count++;
        }
    }

    if (res.added_pins_count == 0 && res.removed_pins_count == 0) {
        res.status = ECO_NO_CHANGE;
    } else {
        res.status = ECO_PINS_MODIFIED;
    }
    return res;
}
