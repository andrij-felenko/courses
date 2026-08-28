#include <cmath>

// Діючий струм вхідного конденсатора buck-перетворювача.
// I — вихідний струм навантаження, A;  D — шпаруватість (0..1).
float cin_rms(float I, float D)
{
    return I * std::sqrt(D * (1.0f - D));   // I·√(D(1−D))
}

// Діючий струм верхнього ключа (прямокутник зі шпаруватістю D).
float highside_rms(float I, float D)
{
    return I * std::sqrt(D);                // I·√D
}
