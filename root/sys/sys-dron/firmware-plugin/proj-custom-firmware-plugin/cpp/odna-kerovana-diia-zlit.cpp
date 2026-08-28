void SokilFirmwarePlugin::guidedModeTakeoff(Vehicle *vehicle, double takeoffAltRel) const
{
    // 1. Чи не відмовився цей борт від команди раніше.
    const auto *data = qobject_cast<SokilFirmwarePluginInstanceData*>(vehicle->firmwarePluginInstanceData());
    if (data && data->getCommandSupported(MAV_CMD_NAV_TAKEOFF)
                == FirmwarePluginInstanceData::CommandSupportedResult::UNSUPPORTED) {
        QGC::showAppMessage(tr("Прошивка цього апарата не приймає команду зльоту."));
        return;
    }

    // 2. Sokil чекає висоту від рівня моря — переводимо, поки знаємо, де стоїмо.
    const double vehicleAltitudeAMSL = vehicle->altitudeAMSL()->rawValue().toDouble();
    if (qIsNaN(vehicleAltitudeAMSL)) {
        QGC::showAppMessage(tr("Зліт неможливий: висота апарата невідома."));
        return;
    }
    const double takeoffAltAMSL = takeoffAltRel + vehicleAltitudeAMSL;

    // 3. Режим — до вмикання моторів: у решті режимів Sokil ігнорує команду зльоту.
    if (!_setFlightModeAndValidate(vehicle, guidedFlightMode())) {
        QGC::showAppMessage(tr("Зліт неможливий: апарат не перейшов у режим Guided."));
        return;
    }

    // 4. Мотори — до команди: без них зліт буде відхилено.
    if (!_armVehicleAndValidate(vehicle)) {
        QGC::showAppMessage(tr("Зліт неможливий: не вдалося ввімкнути мотори."));
        return;
    }

    // 5. І аж тепер сама команда.
    vehicle->sendMavCommand(vehicle->defaultComponentId(),
                            MAV_CMD_NAV_TAKEOFF,
                            true,                                    // показати відмову користувачеві
                            NAN,                                     // тангаж не задаємо
                            NAN, NAN, NAN,                           // не використовуються
                            NAN, NAN,                                // широта й довгота — «де стоїмо»
                            static_cast<float>(takeoffAltAMSL));
}
