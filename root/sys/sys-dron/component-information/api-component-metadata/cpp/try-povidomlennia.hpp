// VehicleTypes.h
typedef void (*RequestMessageResultHandler)(void* resultHandlerData,
                                            MAV_RESULT commandResult,
                                            RequestMessageResultHandlerFailureCode_t failureCode,
                                            const mavlink_message_t& message);

// Vehicle.h
void requestMessage(RequestMessageResultHandler resultHandler, void* resultHandlerData,
                    int compId, int messageId,
                    float param1 = 0.0f, ..., float param5 = 0.0f);
