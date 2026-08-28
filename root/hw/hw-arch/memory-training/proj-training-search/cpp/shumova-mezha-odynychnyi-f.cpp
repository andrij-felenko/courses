// Замазує «діри» з F завдовжки <= max_gap, оточені P з обох боків:
// такі короткі провали — шум на межі ока, а не справжній край.
// map правиться на місці.
void despeckle(bool map[], int n, int max_gap)
{
    int i = 0;
    while (i < n) {
        if (map[i]) { i++; continue; }

        int j = i;                         // початок смуги F
        while (j < n && !map[j]) j++;      // j — перша P після смуги (або n)
        int gap = j - i;                   // довжина смуги F

        bool bounded = (i > 0) && (j < n); // P ліворуч І P праворуч
        if (bounded && gap <= max_gap) {
            for (int k = i; k < j; k++)    // коротка внутрішня діра — затерти
                map[k] = true;
        }
        i = j;                             // йдемо далі від кінця смуги
    }
}
