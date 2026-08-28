// Час приходу (arrival) у кожному вузлі, наносекунди. Прохід УПЕРЕД.
float tcq = 0.6f;                       // clock-to-Q джерел A і B
float aA  = tcq,  aB = tcq;             // A = 0.6 ;  B = 0.6
float aG1 = aA + 1.4f;                  // 0.6 + 1.4 = 2.0
float aG2 = aB + 2.1f;                  // 0.6 + 2.1 = 2.7
float aG3 = std::max(aG1, aG2) + 2.3f;  // max(2.0, 2.7) + 2.3 = 5.0  ← пізній вхід G2 переміг
float aG4 = aG3 + 1.8f;                 // 5.0 + 1.8 = 6.8
float aG5 = aG2 + 0.4f;                 // 2.7 + 0.4 = 3.1
float arrD1 = aG4;                      // на вході D1: 6.8
float arrD2 = aG5;                      // на вході D2: 3.1
