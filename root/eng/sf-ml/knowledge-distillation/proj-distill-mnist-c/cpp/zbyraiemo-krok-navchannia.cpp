// Один крок навчання учня на одному прикладі.
// forward_student(x) заповнює логіти учня; backward_student(grad) розносить
// градієнт крізь ваги; sgd_step() робить крок оптимізатора. Ці три — з коду мережі.
void distill_train_step(const float *x, const float *z_teacher, int y,
                        float T, float alpha, int n) {
    float z_student[16];
    float grad[16];

    forward_student(x, z_student);                           // 1) прямий хід учня
    distill_grad(z_student, z_teacher, y, T, alpha, grad, n);// 2) наш градієнт на логітах
    backward_student(grad);                                  // 3) зворотне поширення учня
    sgd_step();                                              // 4) крок спуску
}
