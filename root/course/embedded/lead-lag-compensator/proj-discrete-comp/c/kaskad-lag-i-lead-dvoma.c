comp_t lag, lead;

void controller_init(void)
{
    // lag: точність на низах (підсилення на низах ×10), фаза майже не чіпається
    comp_init(&lag,  3.0f, 0.3f, 0.001f, 10.0f);   // wz=3, wp=0.3, K=wz/wp=10
    // lead: випередження фази на кросовері (як вище)
    comp_init(&lead, 14.0f, 64.0f, 0.001f, 1.0f);  // wz=14, wp=64, K=1
}

// гарячий такт, 1 кГц:
float controller_step(float setpoint, float y)
{
    float e   = setpoint - y;
    float mid = comp_step(&lag,  e);     // lag обробляє помилку першим
    float u   = comp_step(&lead, mid);   // його вихід живить lead
    return clampf(u, U_MIN, U_MAX);      // насичення на самому виході каскаду
}
