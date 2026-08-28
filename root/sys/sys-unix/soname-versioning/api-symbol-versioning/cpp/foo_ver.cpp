// foo_ver.cpp — Застосування .symver у C++ з обгорткою extern "C"
extern "C" {

int foo_process_v1(int arg) {
    return arg * 2;
}
__asm__(".symver foo_process_v1, foo_process@LIBFOO_1.0");

int foo_process_v2(int arg, int flags) {
    return arg * flags;
}
__asm__(".symver foo_process_v2, foo_process@@LIBFOO_2.0");

}
