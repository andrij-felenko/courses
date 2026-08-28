static const float G = 9.81f;         /* м/с² */
static const float FF = 1.0f;         /* поріг падіння: ~0.1g, м/с² */

/* напрямок тяжіння-реакції, повернутий у поточні осі корпусу */
static vec3 gravity_in_body(quat q) {
    vec3 up = { 0.0f, 0.0f, G };      /* світовий «вгору·g» */
    return quat_rotate(quat_conj(q), up);   /* світ → корпус = обернений q */
}

/* чисте лінійне прискорення руху в осях корпусу */
static vec3 linear_accel(vec3 a_b, quat q) {
    vec3 g = gravity_in_body(q);
    vec3 r = { a_b.x - g.x, a_b.y - g.y, a_b.z - g.z };
    return r;
}

/* вільне падіння: увесь вектор показу майже нульовий */
static int is_free_fall(vec3 a_b) {
    float m2 = a_b.x*a_b.x + a_b.y*a_b.y + a_b.z*a_b.z;
    return m2 < FF * FF;              /* |a_b| < поріг */
}
