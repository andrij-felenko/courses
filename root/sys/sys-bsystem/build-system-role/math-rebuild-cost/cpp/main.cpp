struct Task { double t; std::vector<int> inputs; };   // час і індекси входів

// Вершини вже в топологічному порядку: кожна стоїть після всіх своїх входів.
std::pair<double, double> work_and_span(const std::vector<Task>& g) {
    std::vector<double> finish(g.size(), 0.0);
    double work = 0.0, span = 0.0;
    for (std::size_t v = 0; v < g.size(); ++v) {
        double ready = 0.0;                    // коли готові всі входи
        for (int u : g[v].inputs)
            ready = std::max(ready, finish[u]);
        finish[v] = ready + g[v].t;
        work += g[v].t;
        span = std::max(span, finish[v]);
    }
    return {work, span};
}
