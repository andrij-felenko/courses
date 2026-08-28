int main() {
    LiteModel lite;
    if (!lite.load("model_quant.tflite")) return 2;     // кандидат на чип

    std::vector<TestCase> set = load_test_set("testset.bin");  // кадри + ref + істина
    Report r = evaluate(lite, set);

    Thresholds th;                  // за замовчуванням — помірно строгі
    bool ok = verdict(r, th);

    // Код повернення — щоб CI/скрипт сам зупинив конвеєр, якщо ✗.
    return ok ? 0 : 1;
}
