// Частоти нот у герцах (рівномірна темперація, A4 = 440 Гц).
// Назва = нота + номер октави. #: C#4 пишемо як CS4.
// 4-та октава (найужитковіша для «біпів» і мелодій):
#define NOTE_C4   262
#define NOTE_CS4  277
#define NOTE_D4   294
#define NOTE_DS4  311
#define NOTE_E4   330
#define NOTE_F4   349
#define NOTE_FS4  370
#define NOTE_G4   392
#define NOTE_GS4  415
#define NOTE_A4   440
#define NOTE_AS4  466
#define NOTE_B4   494
// 5-та октава (вдвічі вищі частоти — дзвінкіше, ближче до резонансу пластини):
#define NOTE_C5   523
#define NOTE_D5   587
#define NOTE_E5   659
#define NOTE_F5   698
#define NOTE_G5   784
#define NOTE_A5   880
#define NOTE_B5   988
#define NOTE_C6  1047
// 3-тя октава (нижчі — глухіші на KY-006, бо далі від резонансу ≈2 кГц):
#define NOTE_A3   220
#define NOTE_B3   247
#define REST        0   // тиша (пауза)
