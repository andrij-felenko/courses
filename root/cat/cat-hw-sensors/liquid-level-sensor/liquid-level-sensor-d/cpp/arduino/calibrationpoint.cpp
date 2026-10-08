#include <Arduino.h>

struct CalibrationPoint {
    float heightMm;
    float volumeLiters;
};

class TankVolumeCalculator {
private:
    const CalibrationPoint* lut;
    size_t lutSize;

public:
    TankVolumeCalculator(const CalibrationPoint* table, size_t size) 
        : lut(table), lutSize(size) {}

    float getVolume(float currentHeightMm) const {
        if (lutSize == 0) return 0.0f;
        if (currentHeightMm <= lut[0].heightMm) return lut[0].volumeLiters;
        if (currentHeightMm >= lut[lutSize - 1].heightMm) return lut[lutSize - 1].volumeLiters;

        for (size_t i = 0; i < lutSize - 1; ++i) {
            if (currentHeightMm >= lut[i].heightMm && currentHeightMm <= lut[i + 1].heightMm) {
                float h0 = lut[i].heightMm;
                float h1 = lut[i + 1].heightMm;
                float v0 = lut[i].volumeLiters;
                float v1 = lut[i + 1].volumeLiters;

                return v0 + (v1 - v0) * ((currentHeightMm - h0) / (h1 - h0));
            }
        }
        return 0.0f;
    }
};

// Приклад використання калібрувальної таблиці
const CalibrationPoint tankTable[] = {
    {0.0f, 0.0f}, {100.0f, 45.0f}, {250.0f, 180.0f}, 
    {500.0f, 500.0f}, {750.0f, 820.0f}, {1000.0f, 1000.0f}
};

TankVolumeCalculator calculator(tankTable, 6);
