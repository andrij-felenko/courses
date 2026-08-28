// Біла пляма: найяскравіше в кожному каналі вважаємо білим → тягнемо до 255
int maxR = 0, maxG = 0, maxB = 0;
for (int i = 0; i < N; i++) {
    if (px[i].r > maxR) maxR = px[i].r;
    if (px[i].g > maxG) maxG = px[i].g;
    if (px[i].b > maxB) maxB = px[i].b;
}
double gR = 255.0 / maxR;
double gG = 255.0 / maxG;
double gB = 255.0 / maxB;
