void requestMessage(RequestMessageResultHandler resultHandler, void *resultHandlerData,
                    int compId, int messageId,
                    float param1 = 0.0f, …, float param5 = 0.0f);

typedef enum {
    RequestMessageNoFailure,
    RequestMessageFailureCommandError,
    RequestMessageFailureCommandNotAcked,
    RequestMessageFailureMessageNotReceived,   // підтвердили, але повідомлення не надіслали
    RequestMessageFailureDuplicate,
} RequestMessageResultHandlerFailureCode_t;
