void sendMavCommand(int compId, MAV_CMD command, bool showError,
                    float param1 = 0.0f, …, float param7 = 0.0f);

void sendMavCommandDelayed(int compId, MAV_CMD command, bool showError, int milliseconds,
                           float param1 = 0.0f, …);

void sendMavCommandInt(int compId, MAV_CMD command, MAV_FRAME frame, bool showError,
                       float param1, float param2, float param3, float param4,
                       double param5, double param6, float param7);

void sendMavCommandWithHandler(const MavCmdAckHandlerInfo_t *ackHandlerInfo,
                               int compId, MAV_CMD command,
                               float param1 = 0.0f, …);

void sendMavCommandIntWithHandler(const MavCmdAckHandlerInfo_t *ackHandlerInfo,
                                  int compId, MAV_CMD command, MAV_FRAME frame,
                                  float param1 = 0.0f, …, double param5 = 0.0f, double param6 = 0.0f,
                                  float param7 = 0.0f);

void sendMavCommandWithLambdaFallback(std::function<void()> lambda, int compId, MAV_CMD command,
                                      bool showError, float param1 = 0.0f, …);
void sendMavCommandIntWithLambdaFallback(std::function<void()> lambda, int compId, MAV_CMD command,
                                         MAV_FRAME frame, bool showError, float param1 = 0.0f, …);
