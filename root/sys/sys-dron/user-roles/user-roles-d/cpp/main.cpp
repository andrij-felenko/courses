// Власна збірка під готовий апарат: оператор не прошиває борт,
// не калібрує акселерометр і будує лише прості маршрути з точок.
class CustomOptions : public QGCOptions
{
public:
    explicit CustomOptions(QObject *parent = nullptr) : QGCOptions(parent) {}

    bool showFirmwareUpgrade()        const override { return false; }
    bool showSensorCalibrationAccel() const override { return false; }
    bool missionWaypointsOnly()       const override { return true;  }
};
