type Pkg = { Ca: number; Ce: number; Na: number; Nc: number };

function metrics({ Ca, Ce, Na, Nc }: Pkg) {
  const I = Ce / (Ca + Ce);       // нестабільність: частка вихідних залежностей
  const A = Na / Nc;              // абстрактність: частка абстрактних типів
  const D = Math.abs(A + I - 1);  // відстань до головної послідовності
  return { I, A, D };
}

metrics({ Ca: 30, Ce: 2, Na: 0, Nc: 9 });   // db-gateway → { I: 0.06, A: 0, D: 0.94 }
