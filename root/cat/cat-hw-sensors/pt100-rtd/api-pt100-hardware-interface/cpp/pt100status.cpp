enum class Pt100Status {
    Ok,
    ShortCircuit,
    OpenCircuit
};

Pt100Status validatePt100Resistance(float resistanceOhm) noexcept {
    if (resistanceOhm < 15.0f) {
        return Pt100Status::ShortCircuit;
    }
    if (resistanceOhm > 400.0f) {
        return Pt100Status::OpenCircuit;
    }
    return Pt100Status::Ok;
}
