#include <Arduino.h>
#include <math.h>

class SX1262LinkBudget {
public:
    static float getSnrMin(int sf) {
        if (sf < 7) sf = 7;
        if (sf > 12) sf = 12;
        const float snrTable[] = {-7.5f, -10.0f, -12.5f, -15.0f, -17.5f, -20.0f};
        return snrTable[sf - 7];
    }

    static float calculateFSPL(float distanceKm, float freqMhz) {
        return 20.0f * log10f(distanceKm) + 20.0f * log10f(freqMhz) + 32.44f;
    }

    static float calculateSensitivity(float bandwidthHz, int sf, float noiseFigureDb = 6.0f) {
        return -174.0f + 10.0f * log10f(bandwidthHz) + noiseFigureDb + getSnrMin(sf);
    }

    static float calculateFadeMargin(float pTxDbm, float gTxDbi, float gRxDbi, 
                                     float distanceKm, float freqMhz, 
                                     float bandwidthHz, int sf, 
                                     float lossMiscDb = 2.0f) {
        float fspl = calculateFSPL(distanceKm, freqMhz);
        float pRx = pTxDbm + gTxDbi + gRxDbi - fspl - lossMiscDb;
        float sRx = calculateSensitivity(bandwidthHz, sf);
        return pRx - sRx;
    }
};
