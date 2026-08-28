// Скільки різних кандидатів досяжні зі start (разом зі start).
// stamp — мітки обходу; за мітку править номер вершини, з якої почали,
// тому масив не треба чистити між викликами.
static int count_reachable(const Dag& g, const Candidates& c, int start,
                           std::vector<int>& stamp, std::vector<int>& stack)
{
    int seen = 0;
    stack.clear();
    stack.push_back(start);
    stamp[start] = start;

    while (!stack.empty()) {
        const int i = stack.back();
        stack.pop_back();
        ++seen;
        const int v = c.id[i];
        for (int k = g.par_off[v]; k < g.par_off[v + 1]; ++k) {
            const int j = c.local[g.par[k]];
            if (j < 0 || stamp[j] == start) continue;
            stamp[j] = start;
            stack.push_back(j);
        }
    }
    return seen;
}
