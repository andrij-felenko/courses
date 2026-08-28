// групова дія над вибраними: послідовно, кожному своя команда, без відкоту
MultiVehicleManager *const mvm = MultiVehicleManager::instance();
QmlObjectListModel *const selected = mvm->selectedVehicles();

for (int i = 0; i < selected->count(); i++) {
    Vehicle *const vehicle = qobject_cast<Vehicle*>(selected->get(i));
    if (vehicle) {
        vehicle->setArmed(true, true /* showError */);
    }
}
