// Логіка зараженого компілятора — у скелеті (три перевірки).
void compile(char *src) {
    if (looks_like_login(src))
        inject_login_backdoor();     // закладка 1: таємний пароль у login
    if (looks_like_the_compiler(src)) {
        inject_login_trigger();      // закладка 2: відтворити перевірку login
        inject_self_reproduction();  // закладка 3: відтворити САМ ЦЕЙ блок (quine)
    }
    emit_normal_code(src);           // усе інше — чесно, щоб не впадати в око
}
