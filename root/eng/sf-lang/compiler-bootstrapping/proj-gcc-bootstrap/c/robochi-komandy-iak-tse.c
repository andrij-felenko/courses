// Дерево з джерелами розпаковане у ./gcc-src.
// Крок 0. ОКРЕМА тека збірки (build != source — обов'язково).
mkdir gcc-build && cd gcc-build

// Крок 1. Конфігурація. Для рідної збірки цього досить —
//          триетапний bootstrap увімкнено за замовчуванням.
../gcc-src/configure --prefix=/opt/gcc-new --disable-multilib

// Крок 2. Сам bootstrap. У native-конфігурації просте `make`
//          РОБИТЬ повний триетапний bootstrap; явний target — синонім.
make            // == make bootstrap: stage1 → stage2 → stage3 → compare
