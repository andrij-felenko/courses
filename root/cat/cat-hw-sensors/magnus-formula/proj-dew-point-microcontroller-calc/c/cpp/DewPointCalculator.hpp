#ifndef DEW_POINT_CALCULATOR_HPP
#define DEW_POINT_CALCULATOR_HPP

class DewPointCalculator {
public:
    enum class Method {
        Math,
        Lut,
        FastApprox
    };

    explicit DewPointCalculator(Method method = Method::Math);

    float calculate(float tempC, float humidityRh) const;

private:
    Method method_;
    
    static constexpr float MAGNUS_A = 17.625f;
    static constexpr float MAGNUS_B = 243.04f;

    float calcMath(float temp, float humidity) const;
    float calcLut(float temp, float humidity) const;
    float calcFast(float temp, float humidity) const;
};

#endif // DEW_POINT_CALCULATOR_HPP
