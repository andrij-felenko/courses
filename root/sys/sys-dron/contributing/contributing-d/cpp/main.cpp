// заборонено: у релізі перевірки не буде
Q_ASSERT(vehicle);
vehicle->setArmed(true);

// правильно: захисна перевірка з раннім поверненням, однакова в усіх збірках
if (!vehicle) {
    qCWarning(MyLog) << "no vehicle";
    return;
}
vehicle->setArmed(true);
