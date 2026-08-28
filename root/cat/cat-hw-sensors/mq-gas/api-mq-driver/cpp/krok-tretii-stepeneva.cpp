// Крива газу: {x = lg(ppm), y = lg(Rₛ/R₀) у опорній точці, slope = нахил}.
// Значення для MQ-2 з коду Sandbox Electronics (зняті з графіків даташита).
struct MqCurve { float x, y, slope; };

const MqCurve LPG_CURVE   = { 2.3f, 0.21f, -0.47f };
const MqCurve CO_CURVE    = { 2.3f, 0.72f, -0.34f };
const MqCurve SMOKE_CURVE = { 2.3f, 0.53f, -0.44f };

// Відношення Rₛ/R₀ → ppm за степеневою кривою (у точковій формі).
float mqPpm(float rsR0, const MqCurve& c) {
  // lg(ppm) = x + (lg(Rₛ/R₀) − y) / slope,  далі 10 у цей степінь
  float lgPpm = c.x + (log10f(rsR0) - c.y) / c.slope;
  return powf(10.0f, lgPpm);
}
