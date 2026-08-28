#include <cmath>

// Параметри конкретного JFET (виміряні або з даташита).
struct Jfet {
    float idss;   // струм насичення витоку, А (U_GS = 0)
    float vp;     // напруга відсічки, В — ВІД'ЄМНА (напр. −3.0)
};

/*
 * Опір резистора витоку для бажаного струму self-bias-джерела.
 * Повертає R_S в омах, або −1, якщо струм недосяжний для цього JFET.
 *
 * iTarget — бажаний струм, А (має бути 0 < iTarget ≤ idss)
 */
float sourceResistor(const Jfet &q, float iTarget)
{
    // Нижче за I_DSS опустити можна, вище — ні: за U_GS=0 уже тече
    // рівно I_DSS, а додатну U_GS на керівний перехід подавати не можна.
    if (iTarget <= 0.0f || iTarget > q.idss)
        return -1.0f;

    // Точно I_DSS — це закорочений затвор: R_S = 0.
    if (iTarget == q.idss)
        return 0.0f;

    // Потрібна напруга затвор-витік за квадратичним законом:
    //   U_GS = U_P · (1 − sqrt(I_target / I_DSS))            (В, від'ємна)
    float ugs = q.vp * (1.0f - std::sqrt(iTarget / q.idss));

    // Резистор створює цю напругу падінням від струму:
    //   R_S = −U_GS / I_target                                (Ом)
    return -ugs / iTarget;
}
