void Vehicle::setArmed(bool armed, bool showError)
{
    // саме COMMAND_LONG:MAV_CMD_COMPONENT_ARM_DISARM — його підтримує більше польотних стеків
    sendMavCommand(_defaultComponentId, MAV_CMD_COMPONENT_ARM_DISARM, showError,
                   armed ? 1.0f : 0.0f);
}

void Vehicle::forceArm()
{
    sendMavCommand(_defaultComponentId, MAV_CMD_COMPONENT_ARM_DISARM, true,
                   1.0f,     // зброїти
                   2989);    // домовлене число «попри перевірки»
}
