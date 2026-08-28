// foo_attr.cpp — Застосування атрибута symver у C++
extern "C" {

__attribute__((symver("foo_process@LIBFOO_1.0")))
int foo_process_v1(int arg) {
    return arg * 2;
}

__attribute__((symver("foo_process@@LIBFOO_2.0")))
int foo_process_v2(int arg, int flags) {
    return arg * flags;
}

}
