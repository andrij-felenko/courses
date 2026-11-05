#ifndef HEATER_CONTROLLER_HPP
#define HEATER_CONTROLLER_HPP

class HeaterController {
public:
    HeaterController(float hysteresisC, float safetyMarginC);

    void update(float currentTemp, float dewPoint);
    bool isOn() const;

private:
    bool isOn_ = false;
    float hysteresisC_;
    float safetyMarginC_;
};

#endif // HEATER_CONTROLLER_HPP
