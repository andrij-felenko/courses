// Час-коли-треба (required). Прохід НАЗАД від дедлайну.
float T = 8.0f, tsetup = 0.5f;
float reqD1 = T - tsetup;               // 8.0 − 0.5 = 7.5  (дедлайн на вході D1)
float reqD2 = T - tsetup;               // 7.5             (дедлайн на вході D2)
float rG4 = reqD1;                      // 7.5
float rG3 = rG4 - 1.8f;                 // 7.5 − 1.8 = 5.7
float rG5 = reqD2;                      // 7.5
// G2 живить ДВОХ споживачів (через G3 і через G5) → беремо min:
float rG2 = std::min(rG3 - 2.3f, rG5 - 0.4f); // min(5.7−2.3, 7.5−0.4) = min(3.4, 7.1) = 3.4
float rG1 = rG3 - 2.3f;                 // 5.7 − 2.3 = 3.4
