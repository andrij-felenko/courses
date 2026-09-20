#ifndef DH_ARM_SECURITY_ZONE_H
#define DH_ARM_SECURITY_ZONE_H

#include <stdint.h>

typedef struct {
    const char* zone_id;
    const char* pin_code;
} DhArmSecurityZoneCommand;

typedef enum {
    DH_ARM_STATUS_SUCCESS = 0,
    DH_ARM_STATUS_INVALID_PIN,
    DH_ARM_STATUS_SENSOR_OPEN,
    DH_ARM_STATUS_ZONE_NOT_FOUND
} DhArmZoneStatus;

typedef struct {
    DhArmZoneStatus status;
    const char* zone_id;
} DhArmSecurityZoneResult;

typedef struct DhArmSecurityZoneUseCase DhArmSecurityZoneUseCase;
struct DhArmSecurityZoneUseCase {
    void* context;
    DhArmZoneStatus (*execute)(void* context,
                               const DhArmSecurityZoneCommand* cmd,
                               DhArmSecurityZoneResult* out_result);
};

#endif
