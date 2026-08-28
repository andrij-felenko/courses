struct RebootContext { QPointer<MyWidget> owner; };

static void rebootResultHandler(void *data, int compId,
                                const mavlink_command_ack_t &ack,
                                Vehicle::MavCmdResultFailureCode_t failureCode)
{
    auto *ctx = static_cast<RebootContext*>(data);
    if (failureCode == Vehicle::MavCmdResultCommandResultOnly && ack.result == MAV_RESULT_ACCEPTED) {
        qCDebug(MyLog) << "апарат прийняв перезавантаження";
    } else {
        qCWarning(MyLog) << "відмова:" << MavCommandQueue::failureCodeToString(failureCode);
    }
    delete ctx;                       // обробник викликається рівно один раз
}

void MyWidget::reboot(Vehicle *vehicle)
{
    auto *ctx = new RebootContext{ this };
    Vehicle::MavCmdAckHandlerInfo_t handlerInfo = {};
    handlerInfo.resultHandler     = rebootResultHandler;
    handlerInfo.resultHandlerData = ctx;

    vehicle->sendMavCommandWithHandler(&handlerInfo,
                                       vehicle->defaultComponentId(),
                                       MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN,
                                       1.0f);   // param1: перезавантажити автопілот
}
