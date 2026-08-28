void addVehicleReference() { ++_vehicleReferenceCount; }
void removeVehicleReference();

void LinkInterface::_connectionRemoved()
{
    if (_vehicleReferenceCount == 0) {
        // апаратів на каналі не лишилося — можна рвати просто зараз
        disconnect();
    }
    // інакше чекаємо: решта апаратів іще розмовляє
}
