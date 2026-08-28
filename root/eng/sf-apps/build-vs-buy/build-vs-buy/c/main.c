// Груба, але чесна прикидка TCO на 36 місяців. Головне тут — рахувати
// НЕ цінник, а все життя рішення: старт + супровід за весь горизонт.
const double engineer_month = 10000.0;   // повна вартість місяця інженера, $
const int    horizon        = 36;        // горизонт рішення, місяців

// --- Своє: побудувати й тримати живим ---
double build_start = 2 * 3 * engineer_month;              // 2 інженери × 3 міс
double build_keep  = 0.25 * engineer_month * horizon;     // ¼ інженера/міс супроводу
double build_tco   = build_start + build_keep;

// --- SaaS: підписка + разове налаштування ---
double saas_setup  = 1.0 * 0.25 * engineer_month;         // ~тиждень = ¼ місяця
double saas_fee    = 2000.0 * horizon;                    // $2000/міс × 36
double saas_tco    = saas_setup + saas_fee;

// build_start = 60000 ; build_keep = 90000  -> build_tco = 150000
// saas_setup  =  2500 ; saas_fee   = 72000  -> saas_tco  =  74500
