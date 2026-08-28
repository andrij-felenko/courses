struct Band  { int lo, hi; };
struct OCell { Band o; std::string letters; };   // O-смуга → 4 літери за D-смугами
struct SRow  { Band s; std::vector<OCell> row; }; // S-смуга → рядок O-смуг

constexpr std::array<Band, 4> D_BANDS{{ {7, 10}, {5, 6}, {2, 4}, {1, 1} }};

const std::vector<SRow> AP_POLICY = {
  // S-смуга        O-смуга: клітини за D-смугами   7–10        5–6         2–4         1
  {{9, 10}, {{{8, 10}, "HHHH"}, {{6, 7}, "HHHH"}, {{4, 5}, "HHHH"}, {{2, 3}, "HHHM"}, {{1, 1}, "MMLL"}}},
  {{7,  8}, {{{8, 10}, "HHHH"}, {{6, 7}, "HHHM"}, {{4, 5}, "HMMM"}, {{2, 3}, "MMLL"}, {{1, 1}, "LLLL"}}},
  {{4,  6}, {{{8, 10}, "HHMM"}, {{6, 7}, "MMML"}, {{4, 5}, "MLLL"}, {{2, 3}, "LLLL"}, {{1, 1}, "LLLL"}}},
  {{2,  3}, {{{8, 10}, "MMLL"}, {{6, 7}, "LLLL"}, {{4, 5}, "LLLL"}, {{2, 3}, "LLLL"}, {{1, 1}, "LLLL"}}},
  {{1,  1}, {{{8, 10}, "LLLL"}, {{6, 7}, "LLLL"}, {{4, 5}, "LLLL"}, {{2, 3}, "LLLL"}, {{1, 1}, "LLLL"}}},
};
