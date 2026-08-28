// DR у децибелах і в "ефективних бітах" (стопах)
float full_well   = 30000.0f;   // електронів до насичення
float read_noise  = 6.0f;       // електронів шуму зчитування
float ratio       = full_well / read_noise;        // = 5000

float dr_db       = 20.0f * log10f(ratio);          // 20·log10(5000)
//                = 20 · 3.699  ≈  74.0 дБ

float dr_stops    = log2f(ratio);                   // log2(5000)
//                = ln(5000)/ln(2)  ≈  12.3 стопа (біта)
