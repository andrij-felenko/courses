// На мікроконтролері: оцінка ENOB із виміряного SINAD.
// sinad_db приходить із аналізу спектра (FFT) знятого синуса.
float enob_from_sinad(float sinad_db) {
    return (sinad_db - 1.76f) / 6.02f;   // та сама формула, перевернута
}

// Стеля для номіналу N — щоб бачити недобір:
float snr_ceiling(int n_bits) {
    return 6.02f * n_bits + 1.76f;
}
