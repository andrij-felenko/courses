// Псевдокод SIMD-обчислення NdotL для 8 точок (AVX2)
__m256 nx = _mm256_load_ps(&soa->normX[i]);
__m256 ny = _mm256_load_ps(&soa->normY[i]);
__m256 nz = _mm256_load_ps(&soa->normZ[i]);

__m256 lx = _mm256_set1_ps(light_dir.x);
__m256 ly = _mm256_set1_ps(light_dir.y);
__m256 lz = _mm256_set1_ps(light_dir.z);

// Обчислення скалярного добутку: dot = nx*lx + ny*ly + nz*lz через FMA
__m256 dot = _mm256_mul_ps(nx, lx);
dot = _mm256_fmadd_ps(ny, ly, dot);
dot = _mm256_fmadd_ps(nz, lz, dot);

// Відтинання від'ємних значень: max(0, dot)
__m256 zero = _mm256_setzero_ps();
__m256 ndotl = _mm256_max_ps(zero, dot);
