cat > _probe.c <<'EOF'
int main(void) {
    unsigned long v = 1;
    return (*(char *)&v) ? 0 : 1;   /* перший байт одиниця → little-endian */
}
EOF
if ${CC:-cc} -o _probe _probe.c 2>/dev/null && ./_probe; then
    echo '#define WORDS_BIGENDIAN 0' >> config.h
else
    echo '#define WORDS_BIGENDIAN 1' >> config.h
fi
rm -f _probe _probe.c
