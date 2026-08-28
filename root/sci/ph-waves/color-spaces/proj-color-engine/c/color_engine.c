/* color_engine.c - Ідіоматична реалізація мовою C (C99) */
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    unsigned char r;
    unsigned char g;
    unsigned char b;
} RGB8;

typedef struct {
    float r;
    float g;
    float b;
} RGBLinear;

typedef struct {
    float x;
    float y;
    float z;
} XYZ;

typedef struct {
    float l;
    float a;
    float b;
} Oklab;

typedef struct {
    float l;
    float c;
    float h; /* у градусах [0..360] */
} Oklch;

/* Лінеаризація одного каналу sRGB */
static float srgb_to_linear(unsigned char val) {
    float c = (float)val / 255.0f;
    if (c <= 0.04045f) {
        return c / 12.92f;
    }
    return powf((c + 0.055f) / 1.055f, 2.4f);
}

/* Перетворення sRGB (8-bit) у sRGB Linear */
RGBLinear rgb8_to_linear(RGB8 color) {
    RGBLinear lin;
    lin.r = srgb_to_linear(color.r);
    lin.g = srgb_to_linear(color.g);
    lin.b = srgb_to_linear(color.b);
    return lin;
}

/* Перетворення sRGB Linear у CIE XYZ (D65) */
XYZ linear_to_xyz(RGBLinear lin) {
    XYZ xyz;
    xyz.x = 0.4124564f * lin.r + 0.3575761f * lin.g + 0.1804375f * lin.b;
    xyz.y = 0.2126729f * lin.r + 0.7151522f * lin.g + 0.0721750f * lin.b;
    xyz.z = 0.0193339f * lin.r + 0.1191920f * lin.g + 0.9503041f * lin.b;
    return xyz;
}

/* Перетворення CIE XYZ у Oklab */
Oklab xyz_to_oklab(XYZ xyz) {
    /* Крок 1: Перехід у простір LMS */
    float l_c = 0.8189330101f * xyz.x + 0.3618667424f * xyz.y - 0.1288597137f * xyz.z;
    float m_c = 0.0329845436f * xyz.x + 0.9293118715f * xyz.y + 0.0361456387f * xyz.z;
    float s_c = 0.0482003018f * xyz.x + 0.2643662691f * xyz.y + 0.6338517070f * xyz.z;

    /* Крок 2: Нелінійність (кубічний корінь) */
    float l_p = cbrtf(l_c);
    float m_p = cbrtf(m_c);
    float s_p = cbrtf(s_c);

    /* Крок 3: Перехід у Oklab */
    Oklab lab;
    lab.l = 0.2104542553f * l_p + 0.7936177850f * m_p - 0.0040720468f * s_p;
    lab.a = 1.9779984951f * l_p - 2.4285922050f * m_p + 0.4505937099f * s_p;
    lab.b = 0.0259040371f * l_p + 0.7827717662f * m_p - 0.8086758033f * s_p;
    return lab;
}

/* Перетворення sRGB8 безпосередньо у Oklab */
Oklab rgb8_to_oklab(RGB8 color) {
    RGBLinear lin = rgb8_to_linear(color);
    XYZ xyz = linear_to_xyz(lin);
    return xyz_to_oklab(xyz);
}

/* Перетворення Oklab у полярні координати Oklch */
Oklch oklab_to_oklch(Oklab lab) {
    Oklch lch;
    lch.l = lab.l;
    lch.c = sqrtf(lab.a * lab.a + lab.b * lab.b);
    float h_rad = atan2f(lab.b, lab.a);
    float h_deg = h_rad * (180.0f / (float)M_PI);
    if (h_deg < 0.0f) {
        h_deg += 360.0f;
    }
    lch.h = h_deg;
    return lch;
}

/* Обчислення евклідової відмінності ΔE_OK */
float delta_e_ok(Oklab c1, Oklab c2) {
    float dl = c1.l - c2.l;
    float da = c1.a - c2.a;
    float db = c1.b - c2.b;
    return sqrtf(dl * dl + da * da + db * db);
}

int main(void) {
    RGB8 color1 = {255, 0, 0};   /* Червоний */
    RGB8 color2 = {200, 20, 10}; /* Темно-червоний */

    Oklab lab1 = rgb8_to_oklab(color1);
    Oklab lab2 = rgb8_to_oklab(color2);

    float de = delta_e_ok(lab1, lab2);
    printf("Oklab Color 1: L=%.4f, a=%.4f, b=%.4f\n", lab1.l, lab1.a, lab1.b);
    printf("Oklab Color 2: L=%.4f, a=%.4f, b=%.4f\n", lab2.l, lab2.a, lab2.b);
    printf("Delta E_OK = %.4f (Поріг сприйняття ~0.02)\n", de);

    return 0;
}
