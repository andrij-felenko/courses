enum class Pt100Status {
    Ok,
    OpenCircuit,
    ShortCircuit,
    OutOfRange,
    CalibrationError
};

struct Pt100Result {
    Pt100Status status;
    float temperatureC;
};

Pt100Result readTemperatureSafe(Pt100Driver& driver) {
    float resistance = driver.readResistance();
    if (resistance > 400.0f) return {Pt100Status::OpenCircuit, 0.0f};
    if (resistance < 18.0f)  return {Pt100Status::ShortCircuit, 0.0f};

    float temp = driver.processCvd(resistance);
    if (temp < -200.0f || temp > 850.0f) return {Pt100Status::OutOfRange, temp};

    return {Pt100Status::Ok, temp};
}
