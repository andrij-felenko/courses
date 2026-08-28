namespace app {
void part_overload() {
    head("2. ADL-кандидат перемагає локально видимого");

    lib::Widget       w{7};
    const lib::Widget frozen{8};

    ask("trace(w)       ");  trace(w);
    ask("trace(frozen)  ");  trace(frozen);
    ask("(trace)(w)     ");  (trace)(w);
    ask("app::trace(w)  ");  app::trace(w);
}
}
