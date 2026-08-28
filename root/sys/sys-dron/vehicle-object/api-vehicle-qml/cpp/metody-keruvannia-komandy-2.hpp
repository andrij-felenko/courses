typedef enum {
    MavCmdResultCommandResultOnly,          // у commandResult повна відповідь про успіх або відмову
    MavCmdResultFailureNoResponseToCommand, // апарат не відповів узагалі
    MavCmdResultFailureDuplicateCommand,    // така сама команда вже чекає на відповідь
} MavCmdResultFailureCode_t;

typedef void (*MavCmdResultHandler)(void *resultHandlerData, int compId,
                                    const mavlink_command_ack_t &ack,
                                    MavCmdResultFailureCode_t failureCode);

typedef void (*MavCmdProgressHandler)(void *progressHandlerData, int compId,
                                      const mavlink_command_ack_t &ack);

typedef struct MavCmdAckHandlerInfo_s {
    MavCmdResultHandler   resultHandler;        // nullptr — обробника немає
    void                 *resultHandlerData;
    MavCmdProgressHandler progressHandler;      // ловить MAV_RESULT_IN_PROGRESS
    void                 *progressHandlerData;
} MavCmdAckHandlerInfo_t;
