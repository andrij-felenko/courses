// di/dt на фронті обриву: весь струм спадає за час фронту
//   di/dt = I / t_r = 4 А / 8e-9 с = 5.0e8 А/с  (0.5 А/нс)
const double I   = 4.0;        // А
const double t_r = 8e-9;       // с
double didt = I / t_r;         // = 5.0e8 А/с

// Той самий відтинок ~10 мм, але різна геометрія звороту:
double L_trace = 8.0e-9;       // тонка СПІЛЬНА доріжка  ~8 нГн
double L_plane = 0.8e-9;       // зворот під доріжкою по СУЦІЛЬНІЙ площині ~0.8 нГн

double V_trace = L_trace * didt;   // = 4.0 В  стрибок «нуля»
double V_plane = L_plane * didt;   // = 0.4 В
