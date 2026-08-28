static float re[1024], im[1024];

for (size_t i = 0; i < 1024; i++) {
    re[i] = samples[i] * hann[i];    /* вікно — заздалегідь у таблиці */
    im[i] = 0.0f;
}
fft_radix2(re, im, 1024);

/* найсильніша лінія серед бінів 1 … n/2−1; w_sum — сума ваг вікна */
size_t kmax = 1;
for (size_t k = 2; k < 512; k++)
    if (re[k]*re[k] + im[k]*im[k] > re[kmax]*re[kmax] + im[kmax]*im[kmax])
        kmax = k;

float amp = 2.0f * sqrtf(re[kmax]*re[kmax] + im[kmax]*im[kmax]) / w_sum;
float hz  = kmax * (fs / 1024.0f);          /* крок сітки — fs/N */
