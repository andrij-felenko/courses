struct Vec3 { int32_t x, y, z; };           // 12 байтів — не влазить у регістр

Vec3 make_vector(int a, int b, int c) {
    Vec3 v = { a, b, c };
    return v;               // насправді: записати {a,b,c} за схованою адресою
}

int main() {
    Vec3 p = make_vector(1, 2, 3);   // p — і є те місце, куди функція писала
    return p.x;
}
