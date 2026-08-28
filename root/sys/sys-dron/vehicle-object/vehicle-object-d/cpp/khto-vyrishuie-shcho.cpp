// відповідає за апарат тільки перший автопілот; підвіс і камера мають свої compid
if (componentId != MAV_COMP_ID_AUTOPILOT1) {
    return;
}

switch (vehicleType) {
case MAV_TYPE_GCS:                 // інша наземна станція в мережі
case MAV_TYPE_ONBOARD_CONTROLLER:  // бортовий комп'ютер поруч з автопілотом
case MAV_TYPE_GIMBAL:              // підвіс
case MAV_TYPE_ADSB:                // приймач чужого трафіку
    return;
default:
    break;
}

if (_ignoreVehicleIds.contains(vehicleId) || getVehicleById(vehicleId) || vehicleId == 0) {
    return;
}
