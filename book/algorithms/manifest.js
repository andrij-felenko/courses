window.__BOOKS__ = window.__BOOKS__ || [];
window.__BOOKS__.push(
{
  "type": "book",
  "slug": "algorithms",
  "title": "Алгоритми",
  "sections": [
    {
      "slug": "complexity-computability",
      "title": "Складність",
      "scope": "Теорія обчислюваності та складності: межі обчислюваного, класи задач, нижні оцінки.",
      "topics": [
        { slug: "cantor-pairing-function", title: "Парна функція Кантора", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-cantor-pairing.md", status: "recheck" }] , "hist": [{ file: "hist-cantor-set-theory.md", status: "recheck" }] , "math": [{ file: "math-cantor-bijection-proof.md", status: "recheck" }] , "proj": [{ file: "proj-pairing-engine.md", status: "recheck" }] },
        { slug: "chomsky-hierarchy", title: "Ієрархія Хомського", basic: { status: "empty" }, detailed: { status: "recheck" } , "hist": [{ file: "hist-chomsky-hierarchy.md", status: "recheck" }] , "math": [{ file: "math-lba-decidability.md", status: "recheck" }] , "proj": [{ file: "proj-cyk-parser.md", status: "recheck" }] },
        { slug: "diophantine-sets-dprm", title: "Діофантові множини та теорема ДПРМ", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-diophantine-builder.md", status: "recheck" }] , "hist": [{ file: "hist-dprm-chronology.md", status: "recheck" }] , "math": [{ file: "math-pell-exponential.md", status: "recheck" }] , "proj": [{ file: "proj-diophantine-solver.md", status: "recheck" }] },
        { slug: "koblitz-curves", title: "Аномальні криві Кобліца", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-koblitz-tnaf.md", status: "recheck" }] , "hist": [{ file: "hist-koblitz-anomalous.md", status: "recheck" }] , "math": [{ file: "math-tau-adic-expansion.md", status: "recheck" }] , "proj": [{ file: "proj-tau-naf.md", status: "recheck" }] },
        { slug: "kalmar-elementary-functions", title: "Елементарні функції за Кальмаром", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-elementary-spec.md", status: "recheck" }] , "hist": [{ file: "hist-kalmar-origins.md", status: "recheck" }] , "math": [{ file: "math-kalmar-closure.md", status: "recheck" }] , "proj": [{ file: "proj-elementary-evaluator.md", status: "recheck" }] },
        { slug: "j-invariant", title: "j-інваріант еліптичної кривої", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-jinv-toolkit.md", status: "recheck" }] , "hist": [{ file: "hist-klein-modular.md", status: "recheck" }] , "math": [{ file: "math-isomorphism-proof.md", status: "recheck" }] , "proj": [{ file: "proj-isogeny-graph.md", status: "recheck" }] },
        { slug: "slow-growing-hierarchy", title: "Повільнозростаюча ієрархія", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-sgh-evaluator.md", status: "recheck" }] , "hist": [{ file: "hist-girard-hierarchy.md", status: "recheck" }] , "math": [{ file: "math-slow-growing-proofs.md", status: "recheck" }] , "proj": [{ file: "proj-sgh-evaluator.md", status: "recheck" }] },
        { slug: "veblen-hierarchy", title: "Ієрархія Веблена", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-veblen-tree.md", status: "recheck" }] , "hist": [{ file: "hist-veblen-origins.md", status: "recheck" }] , "math": [{ file: "math-veblen-fixed-points.md", status: "recheck" }] , "proj": [{ file: "proj-veblen-ordinals.md", status: "recheck" }] },
        { slug: "term-rewriting-systems", title: "Системи переписування термів", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-rewriting-engine.md", status: "recheck" }] , "hist": [{ file: "hist-term-rewriting.md", status: "recheck" }] , "math": [{ file: "math-confluence-termination.md", status: "recheck" }] , "proj": [{ file: "proj-knuth-bendix.md", status: "recheck" }] },
        { slug: "minkowski-theorem", title: "Теорема Мінковського про опуклі тіла", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-lattice-geometry.md", status: "recheck" }] , "hist": [{ file: "hist-minkowski-geometry-of-numbers.md", status: "recheck" }] , "math": [{ file: "math-blichfeldt-proof.md", status: "recheck" }] , "proj": [{ file: "proj-minkowski-svp-solver.md", status: "recheck" }] },
        { slug: "side-channel-attacks", title: "Атаки по побічних каналах у криптографії", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-constant-time.md", status: "recheck" }] , "hist": [{ file: "hist-side-channel-attacks.md", status: "recheck" }] , "math": [{ file: "math-side-channel-attacks.md", status: "recheck" }] , "proj": [{ file: "proj-constant-time-crypto.md", status: "recheck" }] },
        { slug: "smt-solvers-lia", title: "SMT-солівери та лінійна арифметика Пресбургера (LIA)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-smt-lib.md", status: "recheck" }] , "hist": [{ file: "hist-presburger-smt.md", status: "recheck" }] , "math": [{ file: "math-presburger-complexity.md", status: "recheck" }] , "proj": [{ file: "proj-lia-solver.md", status: "recheck" }] },
        { slug: "pippenger-algorithm", title: "Алгоритм Піппенджера (MSM)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-msm-engine.md", status: "recheck" }] , "hist": [{ file: "hist-pippenger-monomials.md", status: "recheck" }] , "math": [{ file: "math-lower-bounds.md", status: "recheck" }] , "proj": [{ file: "proj-pippenger-msm.md", status: "recheck" }] },
        { slug: "bounded-arithmetic", title: "Обмежена арифметика Bounded Arithmetic", basic: { status: "empty" }, detailed: { status: "recheck" } },
        { slug: "paley-graphs", title: "Графи Пейлі", basic: { status: "empty" }, detailed: { status: "recheck" } , "hist": [{ file: "hist-paley-hadamard.md", status: "recheck" }] , "math": [{ file: "math-paley-spectrum.md", status: "recheck" }] , "proj": [{ file: "proj-paley-construction.md", status: "recheck" }] },
        { slug: "glv-endomorphism", title: "Ендоморфізм GLV/GLS", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-glv-decomposer.md", status: "recheck" }] , "hist": [{ file: "hist-glv-method.md", status: "recheck" }] , "math": [{ file: "math-babai-reduction.md", status: "recheck" }] , "proj": [{ file: "proj-glv-scalar-mul.md", status: "recheck" }] },
        { slug: "sextic-twist", title: "Шестикратний твіст (Sextic Twist)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-twist-interface.md", status: "recheck" }] , "hist": [{ file: "hist-pairing-twists.md", status: "recheck" }] , "math": [{ file: "math-sextic-transform.md", status: "recheck" }] , "proj": [{ file: "proj-sextic-twist.md", status: "recheck" }] },
        { slug: "konigs-lemma", title: "Лема Кеніґа", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-tree-explorer.md", status: "recheck" }] , "hist": [{ file: "hist-konig-infinity.md", status: "recheck" }] , "math": [{ file: "math-wkl-compactness.md", status: "recheck" }] , "proj": [{ file: "proj-infinite-tree-search.md", status: "recheck" }] },
        { slug: "non-standard-models", title: "Нестандартні моделі", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-nonstandard-model.md", status: "recheck" }] , "hist": [{ file: "hist-skolem-tennenbaum.md", status: "recheck" }] , "math": [{ file: "math-tennenbaum-proof.md", status: "recheck" }] , "proj": [{ file: "proj-nonstandard-sim.md", status: "recheck" }] },
        { slug: "fast-growing-hierarchy", title: "Швидкозростаюча ієрархія", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-fgh-evaluator.md", status: "recheck" }] , "hist": [{ file: "hist-fgh-origins.md", status: "recheck" }] , "math": [{ file: "math-fundamental-sequences.md", status: "recheck" }] , "proj": [{ file: "proj-fgh-evaluator.md", status: "recheck" }] },
        { slug: "ramseys-theorem", title: "Теорема Рамсея", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-ramsey-checker.md", status: "recheck" }] , "hist": [{ file: "hist-ramsey-origin.md", status: "recheck" }] , "math": [{ file: "math-ramsey-bounds.md", status: "recheck" }] , "proj": [{ file: "proj-ramsey-solver.md", status: "recheck" }] },
        { slug: "paris-harrington-theorem", title: "Теорема Паріса — Гаррінгтона", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-ramsey-solver.md", status: "recheck" }] , "hist": [{ file: "hist-paris-harrington.md", status: "recheck" }] , "math": [{ file: "math-strengthened-ramsey.md", status: "recheck" }] , "proj": [{ file: "proj-ramsey-checker.md", status: "recheck" }] },
        { slug: "kolmogorov-complexity", title: "Складність за Колмогоровим", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-compress-distance.md", status: "recheck" }] , "hist": [{ file: "hist-kolmogorov-complexity.md", status: "recheck" }] , "math": [{ file: "math-kolmogorov-incompleteness.md", status: "recheck" }] , "proj": [{ file: "proj-compress-in-practice.md", status: "recheck" }] },
        { slug: "random-walks", title: "Випадкові блукання у графах (Random Walks)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-random-walks.md", status: "recheck" }] , "hist": [{ file: "hist-random-walks.md", status: "recheck" }] , "math": [{ file: "math-random-walks.md", status: "recheck" }] , "proj": [{ file: "proj-random-walks.md", status: "recheck" }] },
        { slug: "expander-graphs", title: "Графи-розширювачі (Expander Graphs)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-expander-graph.md", status: "recheck" }] , "hist": [{ file: "hist-expander-discovery.md", status: "recheck" }] , "math": [{ file: "math-spectral-expansion.md", status: "recheck" }] , "proj": [{ file: "proj-expander-construction.md", status: "recheck" }] },
        { slug: "elliptic-curve-pairings", title: "Спарювання еліптичних кривих (Bilinear Pairings)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-pairing-interface.md", status: "recheck" }] , "hist": [{ file: "hist-pairing-crypto.md", status: "recheck" }] , "math": [{ file: "math-miller-algorithm.md", status: "recheck" }] , "proj": [{ file: "proj-miller-pairing.md", status: "recheck" }] },
        { slug: "graph-isomorphism", title: "Ізоморфізм графів", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-nauty-tracer.md", status: "recheck" }] , "hist": [{ file: "hist-babai-algorithm.md", status: "recheck" }] , "math": [{ file: "math-weisfeiler-leman.md", status: "recheck" }] , "proj": [{ file: "proj-vf2-algorithm.md", status: "recheck" }] },
        { slug: "cryptographic-commitment", title: "Криптографічне зобов'язання (Commitment Scheme)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-cryptographic-commitment.md", status: "recheck" }] , "hist": [{ file: "hist-cryptographic-commitment.md", status: "recheck" }] , "math": [{ file: "math-cryptographic-commitment.md", status: "recheck" }] , "proj": [{ file: "proj-pedersen-commitment.md", status: "recheck" }] },
        { slug: "de-bruijn-graph", title: "Граф де Брейнена", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-debruijn-graph.md", status: "recheck" }] , "hist": [{ file: "hist-debruijn-sequences.md", status: "recheck" }] , "math": [{ file: "math-debruijn-properties.md", status: "recheck" }] , "proj": [{ file: "proj-debruijn-generator.md", status: "recheck" }] },
        { slug: "discrete-logarithm", title: "Проблема дискретного логарифма", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-dlog-interface.md", status: "recheck" }] , "hist": [{ file: "hist-diffie-hellman-dlog.md", status: "recheck" }] , "math": [{ file: "math-pohlig-hellman.md", status: "recheck" }] , "proj": [{ file: "proj-dlog-solvers.md", status: "recheck" }] },
        { slug: "traveling-salesperson-problem", title: "Задача комівояжера", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-tsp-interface.md", status: "recheck" }] , "hist": [{ file: "hist-tsp-history.md", status: "recheck" }] , "math": [{ file: "math-tsp-bounds-formulations.md", status: "recheck" }] , "proj": [{ file: "proj-tsp-algorithms.md", status: "recheck" }] },
        { slug: "eulerian-cycle", title: "Ейлерів цикл", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-eulerian-graph.md", status: "recheck" }] , "hist": [{ file: "hist-konigsberg-bridges.md", status: "recheck" }] , "math": [{ file: "math-euler-hierholzer-theorem.md", status: "recheck" }] , "proj": [{ file: "proj-hierholzer-algorithm.md", status: "recheck" }] },
        { slug: "ldpc-codes", title: "Коди з низькою щільністю перевірок на парність (LDPC)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-ldpc-codec.md", status: "recheck" }] , "hist": [{ file: "hist-gallager-ldpc.md", status: "recheck" }] , "math": [{ file: "math-belief-propagation.md", status: "recheck" }] , "proj": [{ file: "proj-ldpc-decoder.md", status: "recheck" }] },
        { slug: "peano-arithmetic", title: "Арифметика Пеано", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-peano-proof-checker.md", status: "recheck" }] , "hist": [{ file: "hist-peano-dedekind.md", status: "recheck" }] , "math": [{ file: "math-nonstandard-models.md", status: "recheck" }] , "proj": [{ file: "proj-peano-interpreter.md", status: "recheck" }] },
        { slug: "recursively-enumerable-sets", title: "Рекурсивно перелічні множини", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-enumerator-interface.md", status: "recheck" }] , "hist": [{ file: "hist-recursively-enumerable.md", status: "recheck" }] , "math": [{ file: "math-re-equivalence.md", status: "recheck" }] , "proj": [{ file: "proj-dovetailing-enumerator.md", status: "recheck" }] },
        { slug: "dinic-algorithm", title: "Алгоритм Дініца", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-dinic-flow.md", status: "recheck" }] , "hist": [{ file: "hist-dinitz-discovery.md", status: "recheck" }] , "math": [{ file: "math-blocking-flow-bounds.md", status: "recheck" }] , "proj": [{ file: "proj-dinic-solver.md", status: "recheck" }] },
        { slug: "rices-theorem", title: "Теорема Райса", basic: { status: "empty" }, detailed: { status: "recheck" } , "hist": [{ file: "hist-rices-theorem.md", status: "recheck" }] , "math": [{ file: "math-rices-theorem.md", status: "recheck" }] , "proj": [{ file: "proj-rices-theorem.md", status: "recheck" }] },
        { slug: "planar-graph", title: "Планарний граф та теорема Куратовського", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-planarity-checker.md", status: "recheck" }] , "hist": [{ file: "hist-kuratowski-pontryagin.md", status: "recheck" }] , "math": [{ file: "math-euler-formula-bounds.md", status: "recheck" }] , "proj": [{ file: "proj-planarity-test.md", status: "recheck" }] },
        { slug: "chromatic-number", title: "Хроматичне число графа", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-coloring-solver.md", status: "recheck" }] , "hist": [{ file: "hist-chromatic-origins.md", status: "recheck" }] , "math": [{ file: "math-mycielski-brooks.md", status: "recheck" }] , "proj": [{ file: "proj-dsatur-coloring.md", status: "recheck" }] },
        { slug: "codd-relational-model", title: "Реляційна модель даних та теорема Кодда", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-relational-algebra-spec.md", status: "recheck" }] , "hist": [{ file: "hist-codd-ibm.md", status: "recheck" }] , "math": [{ file: "math-codd-theorem-proof.md", status: "recheck" }] , "proj": [{ file: "proj-relational-algebra-interpreter.md", status: "recheck" }] },
        { slug: "l-nl-logspace", title: "Класи складності логарифмічної пам'яті L та NL", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-logspace-transducer.md", status: "recheck" }] , "hist": [{ file: "hist-logspace.md", status: "recheck" }] , "math": [{ file: "math-immerman-szelepcsenyi.md", status: "recheck" }] , "proj": [{ file: "proj-st-connectivity.md", status: "recheck" }] },
        { slug: "pseudorandom-generator", title: "Псевдовипадкові генератори та бар'єр природних доведень", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-prg-interface.md", status: "recheck" }] , "hist": [{ file: "hist-prg-natural-proofs.md", status: "recheck" }] , "math": [{ file: "math-nw-generator-reconstruction.md", status: "recheck" }] , "proj": [{ file: "proj-nw-generator.md", status: "recheck" }] },
        { slug: "finite-fields", title: "Скінченні поля (поля Галуа)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-galois-field.md", status: "recheck" }] , "hist": [{ file: "hist-galois-fields.md", status: "recheck" }] , "math": [{ file: "math-field-extensions.md", status: "recheck" }] , "proj": [{ file: "proj-galois-field-arithmetic.md", status: "recheck" }] },
        { slug: "first-order-logic", title: "Логіка першого порядку та дескриптивна складність", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-fo-structures.md", status: "recheck" }] , "hist": [{ file: "hist-fagin-immerman.md", status: "recheck" }] , "math": [{ file: "math-ehrenfeucht-fraisse.md", status: "recheck" }] , "proj": [{ file: "proj-fo-model-checker.md", status: "recheck" }] },
        { slug: "decision-tree-complexity", title: "Складність дерев рішень", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-tree-complexity-analyzer.md", status: "recheck" }] , "hist": [{ file: "hist-sensitivity-conjecture.md", status: "recheck" }] , "math": [{ file: "math-huang-sensitivity-proof.md", status: "recheck" }] , "proj": [{ file: "proj-decision-tree-evaluator.md", status: "recheck" }] },
        { slug: "dnf-cnf", title: "Диз'юнктивні та кон'юнктивні нормальні форми (ДНФ і КНФ)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-cnf-dnf-ast.md", status: "recheck" }] , "hist": [{ file: "hist-dnf-cnf.md", status: "recheck" }] , "math": [{ file: "math-dnf-cnf-duality.md", status: "recheck" }] , "proj": [{ file: "proj-cnf-dnf-converter.md", status: "recheck" }] },
        { slug: "resolution-proof-system", title: "Система резолюційних виводів (Resolution Proof System)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-proof-format.md", status: "recheck" }] , "hist": [{ file: "hist-resolution.md", status: "recheck" }] , "math": [{ file: "math-completeness.md", status: "recheck" }] , "proj": [{ file: "proj-solver.md", status: "recheck" }] },
        { slug: "watched-literals", title: "Техніка двох спостережуваних літералів (Watched Literals)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-watched-literals-interface.md", status: "recheck" }] , "hist": [{ file: "hist-two-watched-literals.md", status: "recheck" }] , "math": [{ file: "math-watched-literals-invariant.md", status: "recheck" }] , "proj": [{ file: "proj-watched-literals-engine.md", status: "recheck" }] },
        { slug: "dpll-cdcl", title: "Алгоритми DPLL та CDCL у SAT-солверах", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-dpll-cdcl.md", status: "recheck" }] , "hist": [{ file: "hist-dpll-cdcl.md", status: "recheck" }] , "math": [{ file: "math-dpll-cdcl.md", status: "recheck" }] , "proj": [{ file: "proj-dpll-cdcl.md", status: "recheck" }] },
        { slug: "universal-hashing", title: "Універсальне хешування", basic: { status: "recheck" }, detailed: { status: "recheck" } , "api": [{ file: "api-universal-hash-spec.md", status: "recheck" }] , "hist": [{ file: "hist-carter-wegman.md", status: "recheck" }] , "math": [{ file: "math-universal-family.md", status: "recheck" }] , "proj": [{ file: "proj-universal-hash.md", status: "recheck" }] },
        { slug: "fiat-shamir-transform", title: "Евристика Фіата — Шаміра", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-fiat-shamir-transform.md", status: "recheck" }] , "hist": [{ file: "hist-fiat-shamir.md", status: "recheck" }] , "math": [{ file: "math-fiat-shamir-soundness.md", status: "recheck" }] , "proj": [{ file: "proj-fiat-shamir-signature.md", status: "recheck" }] },
        { slug: "zero-knowledge-proofs", title: "Протоколи нульового розголошення", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-zk-verifier.md", status: "recheck" }] , "hist": [{ file: "hist-zkp-origins.md", status: "recheck" }] , "math": [{ file: "math-simulation-paradigm.md", status: "recheck" }] , "proj": [{ file: "proj-schnorr-zkp.md", status: "recheck" }] },
        { slug: "godel-incompleteness", title: "Теорема Ґеделя про неповноту", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-proof-checker.md", status: "recheck" }] , "hist": [{ file: "hist-godel-hilbert.md", status: "recheck" }] , "math": [{ file: "math-diagonalization-proof.md", status: "recheck" }] , "proj": [{ file: "proj-godel-numbering-evaluator.md", status: "recheck" }] },
        { slug: "arithmetic-hierarchy", title: "Арифметична ієрархія", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-arithmetic-oracle.md", status: "recheck" }] , "hist": [{ file: "hist-kleene-hierarchy.md", status: "recheck" }] , "math": [{ file: "math-post-theorem.md", status: "recheck" }] , "proj": [{ file: "proj-formula-classifier.md", status: "recheck" }] },
        { slug: "hamiltonian-cycle", title: "Гамільтонів граф та гамільтонів цикл", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-hamiltonian-solver.md", status: "recheck" }] , "hist": [{ file: "hist-icosian-game.md", status: "recheck" }] , "math": [{ file: "math-dirac-ore-theorems.md", status: "recheck" }] , "proj": [{ file: "proj-backtracking-held-karp.md", status: "recheck" }] },
        { slug: "perfect-matching", title: "Досконале паросполучення", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-matching-solver.md", status: "recheck" }] , "hist": [{ file: "hist-matching-theory.md", status: "recheck" }] , "math": [{ file: "math-tutte-theorem.md", status: "recheck" }] , "proj": [{ file: "proj-matching-algorithms.md", status: "recheck" }] },
        { slug: "adjacency-matrix", title: "Матриця суміжності", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-matrix-interface.md", status: "recheck" }] , "hist": [{ file: "hist-matrix-graph.md", status: "recheck" }] , "math": [{ file: "math-spectral-properties.md", status: "recheck" }] , "proj": [{ file: "proj-graph-matrix.md", status: "recheck" }] },
        { slug: "bipartite-graph", title: "Двочастковий граф", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-bipartite-graph.md", status: "recheck" }] , "hist": [{ file: "hist-bipartite-graphs.md", status: "recheck" }] , "math": [{ file: "math-bipartite-equivalence.md", status: "recheck" }] , "proj": [{ file: "proj-bipartite-checker.md", status: "recheck" }] },
        { slug: "edmonds-algorithm", title: "Алгоритм Едмондса", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-matching-solver.md", status: "recheck" }] , "hist": [{ file: "hist-edmonds-blossoms.md", status: "recheck" }] , "math": [{ file: "math-blossom-duality.md", status: "recheck" }] , "proj": [{ file: "proj-edmonds-matching.md", status: "recheck" }] },
        { slug: "shor-algorithm", title: "Алгоритм Шора", basic: { status: "empty" }, detailed: { status: "recheck" } , "hist": [{ file: "hist-shor-discovery.md", status: "recheck" }] , "math": [{ file: "math-period-finding-qft.md", status: "recheck" }] , "proj": [{ file: "proj-shor-simulation.md", status: "recheck" }] },
        { slug: "bonferroni-inequalities", title: "Нерівності Бонферроні", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-bonferroni-bounds.md", status: "recheck" }] , "hist": [{ file: "hist-bonferroni-origin.md", status: "recheck" }] , "math": [{ file: "math-bonferroni-proof.md", status: "recheck" }] , "proj": [{ file: "proj-bonferroni-solver.md", status: "recheck" }] },
        { slug: "tseytin-transformation", title: "Перетворення Цейтіна", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-dimacs-cnf.md", status: "recheck" }] , "hist": [{ file: "hist-tseytin.md", status: "recheck" }] , "math": [{ file: "math-tseytin-equisatisfiability.md", status: "recheck" }] , "proj": [{ file: "proj-tseytin-encoder.md", status: "recheck" }] },
        { slug: "matrix-permanent", title: "Перманент матриці та складність обчислення", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-matrix-permanent.md", status: "recheck" }] , "hist": [{ file: "hist-valiant-permanent.md", status: "recheck" }] , "math": [{ file: "math-valiant-proof.md", status: "recheck" }] , "proj": [{ file: "proj-ryser-glynn.md", status: "recheck" }] },
        { slug: "ac0-circuits", title: "Клас схем AC0 та схемна складність", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-circuit-dag.md", status: "recheck" }] , "hist": [{ file: "hist-ac0-bounds.md", status: "recheck" }] , "math": [{ file: "math-switching-lemma.md", status: "recheck" }] , "proj": [{ file: "proj-ac0-simulator.md", status: "recheck" }] },
        { slug: "bpp", title: "Клас BPP: ймовірнісні поліноміальні обчислення", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-probabilistic-interface.md", status: "recheck" }] , "hist": [{ file: "hist-bpp.md", status: "recheck" }] , "math": [{ file: "math-error-amplification.md", status: "recheck" }] , "proj": [{ file: "proj-miller-rabin.md", status: "recheck" }] },
        { slug: "turing-degrees", title: "Ступені Тюринга", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-oracle-interface.md", status: "recheck" }] , "hist": [{ file: "hist-turing-degrees.md", status: "recheck" }] , "math": [{ file: "math-priority-method.md", status: "recheck" }] , "proj": [{ file: "proj-oracle-machine.md", status: "recheck" }] },
        { slug: "lattice-cryptography", title: "Решіткова криптографія", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-pqc-standards.md", status: "recheck" }] , "hist": [{ file: "hist-lattice-cryptography.md", status: "recheck" }] , "math": [{ file: "math-lattice-foundations.md", status: "recheck" }] , "proj": [{ file: "proj-lwe-implementation.md", status: "recheck" }] },
        { slug: "natural-proofs", title: "Природні доведення", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-circuit-analyzer.md", status: "recheck" }] , "hist": [{ file: "hist-razborov-rudich.md", status: "recheck" }] , "math": [{ file: "math-razborov-rudich.md", status: "recheck" }] , "proj": [{ file: "proj-pseudo-random-distinguisher.md", status: "recheck" }] },
        { slug: "arthur-merlin-games", title: "Ігри Артура — Мерліна", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-protocol-spec.md", status: "recheck" }] , "hist": [{ file: "hist-interactive-proofs.md", status: "recheck" }] , "math": [{ file: "math-public-vs-private-coins.md", status: "recheck" }] , "proj": [{ file: "proj-graph-nonisomorphism.md", status: "recheck" }] },
        { slug: "chernoff-bound", title: "Нерівність Чернова", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-chernoff-bounds.md", status: "recheck" }] , "hist": [{ file: "hist-chernoff.md", status: "recheck" }] , "math": [{ file: "math-chernoff-derivation.md", status: "recheck" }] , "proj": [{ file: "proj-chernoff-sim.md", status: "recheck" }] },
        { slug: "horn-sat", title: "Задовільненість хорнівських диз'юнктів (Horn-SAT)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-horn-solver.md", status: "recheck" }] , "hist": [{ file: "hist-horn-sat.md", status: "recheck" }] , "math": [{ file: "math-horn-solvability.md", status: "recheck" }] , "proj": [{ file: "proj-horn-solver.md", status: "recheck" }] },
        { slug: "ladner-theorem", title: "Теорема Леднера", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-ladner-reduction.md", status: "recheck" }] , "hist": [{ file: "hist-ladner.md", status: "recheck" }] , "math": [{ file: "math-delayed-simulation.md", status: "recheck" }] , "proj": [{ file: "proj-ladner-simulator.md", status: "recheck" }] },
        { slug: "parity-p", title: "Клас ⊕P (Parity-P)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-parity-interface.md", status: "recheck" }] , "hist": [{ file: "hist-toda-valiant.md", status: "recheck" }] , "math": [{ file: "math-valiant-vazirani.md", status: "recheck" }] , "proj": [{ file: "proj-parity-sat.md", status: "recheck" }] },
        { slug: "p-poly", title: "Клас P/poly: схема складності", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-circuit-builder.md", status: "recheck" }] , "hist": [{ file: "hist-karp-lipton.md", status: "recheck" }] , "math": [{ file: "math-karp-lipton-proof.md", status: "recheck" }] , "proj": [{ file: "proj-circuit-eval.md", status: "recheck" }] },
        { slug: "pspace", title: "Клас PSPACE: поліноміальна пам'ять", basic: { status: "empty" }, detailed: { status: "recheck" } , "hist": [{ file: "hist-pspace.md", status: "recheck" }] , "math": [{ file: "math-savitch.md", status: "recheck" }] , "proj": [{ file: "proj-tqbf-evaluator.md", status: "recheck" }] },
        { slug: "cook-levin-theorem", title: "Теорема Кука — Левіна: фундаментальний камінь NP-повноти", basic: { status: "empty" }, detailed: { status: "recheck" } , "hist": [{ file: "hist-cook-levin.md", status: "done" }] , "math": [{ file: "math-cook-levin-tableau.md", status: "done" }] , "proj": [{ file: "proj-sat-verifier.md", status: "done" }] },
        { slug: "p-vs-np", title: "P проти NP: Головна загадка обчислюваності", basic: { status: "empty" }, detailed: { status: "recheck" } , "hist": [{ file: "hist-p-vs-np.md", status: "done" }] , "math": [{ file: "math-proof-barriers.md", status: "done" }] , "proj": [{ file: "proj-sat-solver.md", status: "done" }] },
        {
          "slug": "state-minimization",
          "title": "Мінімізація скінченного автомата",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-moore-hopcroft.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-myhill-nerode.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-hopcroft.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "fmea",
          "title": "FMEA: аналіз видів і наслідків відмов",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-fmea.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-rpn-ordinal.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-fmea-rpn.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "loop-variant",
          "title": "Варіант циклу",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-termination-proofs.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-well-founded.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-variant-bounds.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "halting-problem",
          "title": "Проблема зупинки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-halting-problem.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-undecidability.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-halting-in-code.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "fault-tree-analysis",
          "title": "Аналіз дерева відмов (FTA)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-fta.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-sharp-p-hardness.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-fault-tree-eval.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "asymptotic-complexity",
          "title": "Асимптотична складність (нотація O великого)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-bachmann-landau.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-formal-bigo.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-doubling-experiment.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "np-completeness",
          "title": "Класи P і NP та NP-повнота",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-classes.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-verify-reduce.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "amortized-analysis",
          "title": "Амортизований аналіз",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-amortized.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-potential-method.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-dynamic-array.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "sharp-p-counting",
          "title": "Клас #P: складність підрахунку розв'язків",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-valiant.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-permanent-determinant.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-permanent-ryser.md",
              "status": "done"
            },
            {
              "file": "proj-sharp-sat-counter.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "master-theorem",
          "title": "Основна теорема про рекурентні співвідношення (master theorem)",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "empty"
          },
          "hist": [
            {
              "file": "hist-master-theorem.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-master-classify.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "polynomial-hierarchy",
          "title": "Поліноміальна ієрархія (PH)",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-polynomial-hierarchy.md",
              "status": "done",
          "math": [
            {
              "file": "math-ph-collapse.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-qsat-solver.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-polynomial-hierarchy.md",
              "status": "done",
          "math": [
            {
              "file": "math-ph-collapse.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-qsat-solver.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "pp-probabilistic-polynomial",
          "title": "Клас PP: ймовірнісний поліноміальний час",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-gill-toda.md",
              "status": "done",
          "math": [
            {
              "file": "math-pp-properties.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-majsat-solver.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-gill-toda.md",
              "status": "done",
          "math": [
            {
              "file": "math-pp-properties.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-majsat-solver.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "comparison-sort-lower-bound",
          "title": "Нижня межа сортування порівняннями (Ω(n log n))",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-sorting-lower-bound.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-decision-tree-sort.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-linear-sort-radix.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "online-competitive-analysis",
          "title": "Онлайнові алгоритми й конкурентний аналіз",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-online-algorithms.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-competitive-ratio.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-online-paging.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "math",
          "title": "math",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "empty"
          }
        }
      ]
    },
    {
      "slug": "design-paradigms",
      "title": "Парадигми",
      "scope": "Загальні методи побудови алгоритмів — каркаси розв'язків для широких класів задач.",
      "topics": [
        {
          "slug": "backpressure",
          "title": "Протитиск (backpressure)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-backpressure.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-queue-stability.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-backpressure-demo.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "ransac",
          "title": "RANSAC: згода на випадковій вибірці",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-ransac.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-iterations.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-ransac-linefit.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "divide-and-conquer",
          "title": "Розділяй і володарюй",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-divide-and-conquer.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-recurrence.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-mergesort.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "memoization",
          "title": "Мемоізація",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-memo-functions.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-subproblem-count.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-edit-distance.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "dynamic-programming",
          "title": "Динамічне програмування",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-bellman.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-optimal-substructure.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-knapsack.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "greedy-algorithms",
          "title": "Жадібні алгоритми",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-greedy-algorithms.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-matroid-greedy.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-greedy-examples.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "backtracking",
          "title": "Пошук із поверненням (backtracking)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-backtracking.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-state-space-tree.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-backtracking-nqueens.md",
              "status": "done"
            }
          ]
        }
      ]
    },
    {
      "slug": "data-structures",
      "title": "Структури",
      "scope": "Організація даних для доступу й оновлення (дерева, купи, хеш, персистентні) разом із упорядкуванням, селекцією та пошуком.",
      "topics": [
        { slug: "cuckoo-hashing", title: "Хешування зозулею (Cuckoo Hashing)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-cuckoo-map.md", status: "recheck" }] , "hist": [{ file: "hist-cuckoo-birth.md", status: "recheck" }] , "math": [{ file: "math-cuckoo-graph.md", status: "recheck" }] , "proj": [{ file: "proj-cuckoo-table.md", status: "recheck" }] },
        { slug: "buddy-allocator", title: "Алокатор двійкових близнюків (Buddy Allocator)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-buddy-allocator.md", status: "recheck" }] , "hist": [{ file: "hist-buddy-allocator.md", status: "recheck" }] , "math": [{ file: "math-buddy-arithmetic.md", status: "recheck" }] , "proj": [{ file: "proj-buddy-c.md", status: "recheck" }] },
        { slug: "reservoir-sampling", title: "Вибірка з резервуара (Reservoir Sampling)", basic: { status: "empty" }, detailed: { status: "recheck" } , "hist": [{ file: "hist-reservoir-sampling.md", status: "recheck" }] , "math": [{ file: "math-reservoir-proof.md", status: "recheck" }] , "proj": [{ file: "proj-reservoir-stream.md", status: "recheck" }] },
        { slug: "popcount", title: "Операція Popcount", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-popcount.md", status: "recheck" }] , "hist": [{ file: "hist-popcount.md", status: "recheck" }] , "math": [{ file: "math-popcount.md", status: "recheck" }] , "proj": [{ file: "proj-rank-bitset.md", status: "recheck" }] },
        { slug: "inverted-index", title: "Інвертований індекс", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "levenshtein-distance", title: "Відстань Левенштейна", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "heavy-light-decomposition", title: "Heavy-Light декомпозиція (HLD)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "kadane-algorithm", title: "Алгоритм Кадане (Kadane's Algorithm)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "binary-heap", title: "Двійкова купа (Binary Heap)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "skip-list", title: "Пропускний список (Skip List)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "sparse-table", title: "Таблиця заміни (Sparse Table)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "harmonic-numbers", title: "Гармонічні числа", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-harmonic-eval.md", status: "recheck" }] , "hist": [{ file: "hist-harmonic-series.md", status: "recheck" }] , "math": [{ file: "math-euler-maclaurin.md", status: "recheck" }] , "proj": [{ file: "proj-harmonic-computation.md", status: "recheck" }] },
        { slug: "catalan-numbers", title: "Числа Каталана", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-catalan-utils.md", status: "recheck" }] , "hist": [{ file: "hist-catalan.md", status: "recheck" }] , "math": [{ file: "math-catalan-proofs.md", status: "recheck" }] , "proj": [{ file: "proj-catalan-algorithms.md", status: "recheck" }] },
        { slug: "segment-tree", title: "Відрізкове дерево (Segment Tree)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-segment-tree.md", status: "recheck" }] , "hist": [{ file: "hist-segment-tree.md", status: "recheck" }] , "math": [{ file: "math-segment-tree.md", status: "recheck" }] , "proj": [{ file: "proj-segment-tree.md", status: "recheck" }] },
        { slug: "cosine-distance", title: "Косинусна відстань", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-cosine-metrics.md", status: "recheck" }] , "hist": [{ file: "hist-cosine-distance.md", status: "recheck" }] , "math": [{ file: "math-cosine-properties.md", status: "recheck" }] , "proj": [{ file: "proj-simd-cosine.md", status: "recheck" }] },
        { slug: "jaccard-index", title: "Індекс Жаккара", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-jaccard-engine.md", status: "recheck" }] , "hist": [{ file: "hist-jaccard.md", status: "recheck" }] , "math": [{ file: "math-jaccard-properties.md", status: "recheck" }] , "proj": [{ file: "proj-jaccard-search.md", status: "recheck" }] },
        { slug: "k-nearest-neighbors", title: "Пошук найближчих сусідів (k-NN)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "timsort", title: "Timsort", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "insertion-sort", title: "Сортування вставками (Insertion Sort)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "bubble-sort", title: "Сортування бульбашкою (Bubble Sort)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "splay-tree", title: "Splay-дерево", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "treap", title: "Декартове дерево (Treap)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "2-3-4-tree", title: "2-3-4 дерево", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "percolation-theory", title: "Теорія перколації", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "hoshen-kopelman", title: "Алгоритм Гошена–Копельмана", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "ribbon-filter", title: "Стрічковий фільтр (Ribbon Filter)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "counting-bloom-filter", title: "Підрахунковий фільтр Блума (Counting Bloom Filter)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "cuckoo-filter", title: "Фільтр Кукушки (Cuckoo Filter)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "shunting-yard", title: "Сортувальна станція Дейкстри", basic: { status: "empty" }, detailed: { status: "pending" } },
        {
          "slug": "bit-flips",
          "title": "Перевернуті біти",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-bit-flip-election.md",
              "status": "done"
            },
            {
              "file": "hist-hamming.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "wear-leveling",
          "title": "Вирівнювання зносу флешу",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-wear-leveling.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-endurance.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-wear-leveling.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "ftl-flash-translation",
          "title": "Шар трансляції флешу (FTL)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-ftl-birth.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-ftl-sim-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "np-hard-placement",
          "title": "NP-важкість задачі розміщення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-placement-annealing.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-placement-nphard.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-annealing-placer.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "logic-synthesis",
          "title": "Логічний синтез: від булевого виразу до LUT-дерева",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-bdd.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-bdd-build.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "cache-oblivious",
          "title": "Кеш-незалежні алгоритми",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-ideal-cache.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-matmul.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "scatter-gather",
          "title": "Scatter-gather DMA",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-scatter-gather-lineage.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-sglist-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "ring-buffer",
          "title": "Кільцевий буфер",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-ring-buffer-indexing.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-ring-buffer-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "key-value-store",
          "title": "Сховище «ключ — значення»",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-associative-to-dynamo.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-load-factor.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-hash-kv-store.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "priority-queue",
          "title": "Черга з пріоритетом (купа)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-heap-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-heap-analysis.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-binary-heap.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "ecc-memory",
          "title": "ECC і виявлення помилок у пам'яті",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-syndrome-and-sizing.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-syndrome-decoder.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "copy-on-write",
          "title": "Copy-on-write: принцип незмінних копій",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-cow-lineage.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-path-copying.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-persistent-bst.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "queue-fifo",
          "title": "Черга: FIFO і кільцевий буфер",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-queue-discipline.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-two-stack-queue.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "recursion",
          "title": "Рекурсія",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-recursion.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-recurrence.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-recursion-to-iteration.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "sorting-networks",
          "title": "Сортувальні мережі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-sorting-networks.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-zero-one-principle.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-bitonic-sort.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "rolling-hash",
          "title": "Ковзний хеш (rolling hash)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-rabin-karp.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-poly-hash-mod.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-rolling-hash-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "over-provisioning",
          "title": "Over-provisioning",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-capacity-interface.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-over-provisioning.md",
              "status": "done",
          "math": [
            {
              "file": "math-amortized-growth.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-over-provisioning.md",
              "status": "done",
          "api": [
            {
              "file": "api-capacity-interface.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-over-provisioning.md",
              "status": "done",
          "math": [
            {
              "file": "math-amortized-growth.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-over-provisioning.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "binary-search",
          "title": "Двійковий пошук",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-binary-search.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-log-complexity.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-binary-search-variants.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "write-amplification",
          "title": "Write Amplification Factor",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-waf-metrics.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-waf-origins.md",
              "status": "done",
          "math": [
            {
              "file": "math-waf-bounds.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-waf-simulator.md",
              "status": "done",
          "api": [
            {
              "file": "api-waf-metrics.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-waf-origins.md",
              "status": "done",
          "math": [
            {
              "file": "math-waf-bounds.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-waf-simulator.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "flash-garbage-collection",
          "title": "Garbage collection у Flash-сховищах",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-gc-trim.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-gc-algorithms.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-gc-simulator.md",
              "status": "done",
          "api": [
            {
              "file": "api-gc-trim.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-gc-algorithms.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-gc-simulator.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "abstract-syntax-tree",
          "title": "Абстрактне синтаксичне дерево (AST)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-ast-evolution.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-tree-traversal.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-ast-parser.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "lsm-tree",
          "title": "B-tree vs LSM-tree / log-structured",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-lsm-origin.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-write-amplification.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-lsm-engine.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "consistent-hashing",
          "title": "Консистентне хешування",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-consistent-hashing.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-ring-distribution.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-consistent-hash-ring.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "merkle-tree",
          "title": "Дерево Меркла",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-merkle-tree.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-merkle.md",
              "status": "done",
          "math": [
            {
              "file": "math-merkle-proof.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-merkle-tree.md",
              "status": "done",
          "api": [
            {
              "file": "api-merkle-tree.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-merkle.md",
              "status": "done",
          "math": [
            {
              "file": "math-merkle-proof.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-merkle-tree.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "bloom-filter",
          "title": "Фільтр Блума",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-bloom-filter.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-bloom-filter.md",
              "status": "done",
          "math": [
            {
              "file": "math-false-positive.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-bloom-filter.md",
              "status": "done",
          "api": [
            {
              "file": "api-bloom-filter.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-bloom-filter.md",
              "status": "done",
          "math": [
            {
              "file": "math-false-positive.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-bloom-filter.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "b-tree",
          "title": "B-дерево",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-b-tree.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-b-tree.md",
              "status": "done",
          "math": [
            {
              "file": "math-b-tree-bounds.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-b-tree.md",
              "status": "done",
          "api": [
            {
              "file": "api-b-tree.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-b-tree.md",
              "status": "done",
          "math": [
            {
              "file": "math-b-tree-bounds.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-b-tree.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "binary-decision-diagram",
          "title": "Двійкова діаграма рішень (BDD)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-model-checking.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-canonicity.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-apply.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "hash-table",
          "title": "Хеш-таблиця",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-hashing-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-open-addressing.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-open-addressing.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "binary-search-tree",
          "title": "Двійкове дерево пошуку (BST)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-bst-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-bst-height.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-bst-operations.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "union-find",
          "title": "Система неперетинних множин (union-find)",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-dsu.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-disjoint-sets.md",
              "status": "done",
          "math": [
            {
              "file": "math-ackermann-analysis.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-dsu-impl.md",
              "status": "done",
          "api": [
            {
              "file": "api-dsu.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-disjoint-sets.md",
              "status": "done",
          "math": [
            {
              "file": "math-ackermann-analysis.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-dsu-impl.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "binary-tree",
          "title": "Двійкове дерево",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-binary-tree.md",
              "status": "done",
          "math": [
            {
              "file": "math-binary-tree.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-binary-tree.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-binary-tree.md",
              "status": "done",
          "math": [
            {
              "file": "math-binary-tree.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-binary-tree.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "heapsort",
          "title": "Сортування купою (heapsort)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-heapsort.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-heapsort.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-heapsort.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "fibonacci-heap",
          "title": "Фібоначчієва купа",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-fredman-tarjan.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-fibonacci-bound.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-fib-heap.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "deque",
          "title": "Двобічна черга (deque)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-deque-origin.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-amortized-deque.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-circular-deque.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "single-event-upset",
          "title": "Одиничний збій від частинки (SEU і SEL)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "array",
          "title": "Масив",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-array-vector.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-array.md",
              "status": "done",
          "math": [
            {
              "file": "math-array-addressing.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-array-operations.md",
              "status": "done",
          "api": [
            {
              "file": "api-array-vector.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-array.md",
              "status": "done",
          "math": [
            {
              "file": "math-array-addressing.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-array-operations.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "linked-list",
          "title": "Зв'язаний список",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-linked-list.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-linked-list.md",
              "status": "done",
          "math": [
            {
              "file": "math-pointer-chasing.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-doubly-linked-list.md",
              "status": "done",
          "api": [
            {
              "file": "api-linked-list.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-linked-list.md",
              "status": "done",
          "math": [
            {
              "file": "math-pointer-chasing.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-doubly-linked-list.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "tree-rotation",
          "title": "Обертання дерева",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-tree-rotation.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-tree-rotation.md",
              "status": "done",
          "math": [
            {
              "file": "math-rotation-invariants.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-tree-rotation.md",
              "status": "done",
          "api": [
            {
              "file": "api-tree-rotation.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-tree-rotation.md",
              "status": "done",
          "math": [
            {
              "file": "math-rotation-invariants.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-tree-rotation.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "avl-tree",
          "title": "AVL-дерево",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-interface.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-avl.md",
              "status": "done",
          "math": [
            {
              "file": "math-height-bound.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-avl-tree.md",
              "status": "done",
          "api": [
            {
              "file": "api-interface.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-avl.md",
              "status": "done",
          "math": [
            {
              "file": "math-height-bound.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-avl-tree.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "red-black-tree",
          "title": "Червоно-чорне дерево",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-rbt.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-rbt.md",
              "status": "done",
          "math": [
            {
              "file": "math-rb-bounds.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-rbt-impl.md",
              "status": "done",
          "api": [
            {
              "file": "api-rbt.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-rbt.md",
              "status": "done",
          "math": [
            {
              "file": "math-rb-bounds.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-rbt-impl.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "quicksort",
          "title": "Швидке сортування (quicksort)",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-quicksort.md",
              "status": "done",
          "math": [
            {
              "file": "math-quicksort.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-quicksort.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-quicksort.md",
              "status": "done",
          "math": [
            {
              "file": "math-quicksort.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-quicksort.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "selection-sort",
          "title": "Сортування вибором (selection sort)",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-selection-sort.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-selection-sort.md",
              "status": "done",
          "math": [
            {
              "file": "math-selection-sort.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-selection-sort.md",
              "status": "done",
          "api": [
            {
              "file": "api-selection-sort.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-selection-sort.md",
              "status": "done",
          "math": [
            {
              "file": "math-selection-sort.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-selection-sort.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "binomial-heap",
          "title": "Біноміальна купа",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-binomial-heap.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-binomial-heap.md",
              "status": "done",
          "math": [
            {
              "file": "math-binomial-tree.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-binomial-heap.md",
              "status": "done",
          "api": [
            {
              "file": "api-binomial-heap.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-binomial-heap.md",
              "status": "done",
          "math": [
            {
              "file": "math-binomial-tree.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-binomial-heap.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "spatial-index",
          "title": "Просторовий індекс: R-дерево і квадродерево",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-spatial-index-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-window-query-cost.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-rtree-insert.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "z-order-curve",
          "title": "Крива Мортона (Z-порядок): просторова близькість у лінійному ключі",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-z-order.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-morton.md",
              "status": "done",
          "math": [
            {
              "file": "math-morton.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-z-order.md",
              "status": "done",
          "api": [
            {
              "file": "api-z-order.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-morton.md",
              "status": "done",
          "math": [
            {
              "file": "math-morton.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-z-order.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "hash-array-mapped-trie",
          "title": "Геш-дерево з бітовими мапами (HAMT)",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-hamt.md",
              "status": "done",
          "math": [
            {
              "file": "math-hamt-popcount.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-hamt.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-hamt.md",
              "status": "done",
          "math": [
            {
              "file": "math-hamt-popcount.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-hamt.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "timer-wheel",
          "title": "Колесо таймерів",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-timer-wheel.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-timer-wheel.md",
              "status": "done",
          "math": [
            {
              "file": "math-timer-wheel.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-timer-wheel.md",
              "status": "done",
          "api": [
            {
              "file": "api-timer-wheel.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-timer-wheel.md",
              "status": "done",
          "math": [
            {
              "file": "math-timer-wheel.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-timer-wheel.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "non-cryptographic-hash",
          "title": "Некриптографічні хеш-функції: FNV, Murmur, xxHash",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-hash-bench.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-hash-functions.md",
              "status": "done",
          "math": [
            {
              "file": "math-avalanche-distribution.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-fast-hash.md",
              "status": "done",
          "api": [
            {
              "file": "api-hash-bench.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-hash-functions.md",
              "status": "done",
          "math": [
            {
              "file": "math-avalanche-distribution.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-fast-hash.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "sorting-stability",
          "title": "Стійкість сортування",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-sorting-stability.md",
              "status": "done",
          "math": [
            {
              "file": "math-stability-proofs.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-stable-sorting.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-sorting-stability.md",
              "status": "done",
          "math": [
            {
              "file": "math-stability-proofs.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-stable-sorting.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "interval-tree",
          "title": "Дерево інтервалів: які відрізки накривають задану точку",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-interval-tree.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-interval-tree.md",
              "status": "done",
          "math": [
            {
              "file": "math-interval-correctness.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-interval-tree.md",
              "status": "done",
          "api": [
            {
              "file": "api-interval-tree.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-interval-tree.md",
              "status": "done",
          "math": [
            {
              "file": "math-interval-correctness.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-interval-tree.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "raid-levels",
          "title": "RAID: смуги, дзеркала й парність",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-linux-md.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-raid-history.md",
              "status": "done",
          "math": [
            {
              "file": "math-parity-gf28.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-raid-simulator.md",
              "status": "done",
          "api": [
            {
              "file": "api-linux-md.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-raid-history.md",
              "status": "done",
          "math": [
            {
              "file": "math-parity-gf28.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-raid-simulator.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "kd-tree",
          "title": "kd-дерево: поділ площини по черзі за координатами",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-kd-tree-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-kd-range-cost.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-kd-nearest.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "quickselect",
          "title": "Швидкий вибір: k-й за порядком за лінійний час",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-quickselect.md",
              "status": "done",
          "math": [
            {
              "file": "math-quickselect.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-quickselect.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-quickselect.md",
              "status": "done",
          "math": [
            {
              "file": "math-quickselect.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-quickselect.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "locality-sensitive-hashing",
          "title": "Локально чутливе хешування (LSH): близькі точки в один кошик",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-lsh.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-lsh.md",
              "status": "done",
          "math": [
            {
              "file": "math-lsh-family.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-lsh-index.md",
              "status": "done",
          "api": [
            {
              "file": "api-lsh.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-lsh.md",
              "status": "done",
          "math": [
            {
              "file": "math-lsh-family.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-lsh-index.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        }
      ]
    },
    {
      "slug": "graph-algorithms",
      "title": "Графові",
      "scope": "Обхід, шляхи, потоки, паросполучення та структурний аналіз графів і мереж.",
      "topics": [
        { slug: "minimum-spanning-tree", title: "Мінімальне кістякове дерево", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "dominator-tree", title: "Дерево домінування (Dominator Tree)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "single-static-assignment", title: "Форма єдиного статичного присвоєння (SSA)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "control-flow-graph", title: "Граф потоку керування (CFG)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "maximum-flow", title: "Задача про максимальний потік", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "edmonds-blossom-algorithm", title: "Алгоритм Едмондса (Blossom Algorithm)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "floyd-warshall", title: "Алгоритм Флойда–Уоршелла", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "graph-dfs-bfs", title: "Обходи графів DFS та BFS", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "graph-representations", title: "Способи представлення графів", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "graph-representation", title: "Представлення графів: матриця та списки суміжності", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "kruskal-algorithm", title: "Алгоритм Краскала", basic: { status: "empty" }, detailed: { status: "pending" } },
        {
          "slug": "routing-algorithms",
          "title": "Алгоритми маршрутизації",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-routing-protocols.md",
              "status": "done",
          "math": [
            {
              "file": "math-dv-convergence.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-distance-vector.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-routing-protocols.md",
              "status": "done",
          "math": [
            {
              "file": "math-dv-convergence.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-distance-vector.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "congestion-control",
          "title": "Управління перевантаженням мережі",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-traffic-shaper.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-congestion-control.md",
              "status": "done",
          "math": [
            {
              "file": "math-maxmin.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-backpressure-routing.md",
              "status": "done",
          "api": [
            {
              "file": "api-traffic-shaper.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-congestion-control.md",
              "status": "done",
          "math": [
            {
              "file": "math-maxmin.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-backpressure-routing.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "dijkstra",
          "title": "Алгоритм Дейкстри",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-dijkstra.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "topological-sort",
          "title": "Топологічне сортування",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-topological-sort.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-topological-sort.md",
              "status": "done"
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "strongly-connected-components",
          "title": "Сильно зв'язні компоненти",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-scc.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-strongly-connected-components.md",
              "status": "done",
          "math": [
            {
              "file": "math-scc-condensation.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-tarjan-scc.md",
              "status": "done",
          "api": [
            {
              "file": "api-scc.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-strongly-connected-components.md",
              "status": "done",
          "math": [
            {
              "file": "math-scc-condensation.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-tarjan-scc.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "register-allocation",
          "title": "Розподіл регістрів",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-register-allocation.md",
              "status": "done",
          "math": [
            {
              "file": "math-register-allocation.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-register-allocation.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-register-allocation.md",
              "status": "done",
          "math": [
            {
              "file": "math-register-allocation.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-register-allocation.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "bellman-ford",
          "title": "Алгоритм Беллмана–Форда",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-bellman-ford.md",
              "status": "done",
          "math": [
            {
              "file": "math-bellman-ford.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-bellman-ford.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-bellman-ford.md",
              "status": "done",
          "math": [
            {
              "file": "math-bellman-ford.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-bellman-ford.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "bipartite-matching",
          "title": "Двочасткові графи й досконале паросполучення",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-bipartite-matching.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-bipartite-matching.md",
              "status": "done",
          "math": [
            {
              "file": "math-könig-hall.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-kuhn-matching.md",
              "status": "done",
          "api": [
            {
              "file": "api-bipartite-matching.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-bipartite-matching.md",
              "status": "done",
          "math": [
            {
              "file": "math-könig-hall.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-kuhn-matching.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "breadth-first-search",
          "title": "Пошук у ширину (BFS)",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-bfs-traversal.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-breadth-first-search.md",
              "status": "done",
          "math": [
            {
              "file": "math-bfs-correctness.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-bfs-applications.md",
              "status": "done",
          "api": [
            {
              "file": "api-bfs-traversal.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-breadth-first-search.md",
              "status": "done",
          "math": [
            {
              "file": "math-bfs-correctness.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-bfs-applications.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "depth-first-search",
          "title": "Пошук у глибину (DFS)",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-dfs.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-dfs.md",
              "status": "done",
          "math": [
            {
              "file": "math-dfs.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-dfs.md",
              "status": "done",
          "api": [
            {
              "file": "api-dfs.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-dfs.md",
              "status": "done",
          "math": [
            {
              "file": "math-dfs.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-dfs.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "transitive-closure",
          "title": "Транзитивне замикання графа",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-reachability.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-warshall.md",
              "status": "done",
          "math": [
            {
              "file": "math-boolean-algebra.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-transitive-closure.md",
              "status": "done",
          "api": [
            {
              "file": "api-reachability.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-warshall.md",
              "status": "done",
          "math": [
            {
              "file": "math-boolean-algebra.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-transitive-closure.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        }
      ]
    },
    {
      "slug": "string-geometry-streaming",
      "title": "Дискретні",
      "scope": "Алгоритми над текстом, геометрією та потоками: пошук і вирівнювання рядків, оболонки й перетини фігур, онлайн-рішення та один прохід над масивними даними.",
      "topics": [
        {
          "slug": "regex-engine",
          "title": "Рушій регулярних виразів",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-regex-engine.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-regex-engine.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-regex-engine.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-regex-engine.md",
              "status": "done"
            }
          ],
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "count-min-sketch",
          "title": "Count-Min Sketch: приблизні лічильники частот за фіксовану пам'ять",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "polygon-offset",
          "title": "Зсув контуру (еквідистанта): розширення й звуження многокутника та ламаної",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "polyline-simplification",
          "title": "Спрощення ламаної: Дуглас–Пекер і жадібні проходи",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "convex-hull",
          "title": "Опукла оболонка множини точок",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "sweep-line",
          "title": "Замітальна пряма: події, статус і геометрія за один прохід",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "curse-of-dimensionality",
          "title": "Прокляття розмірності: чому геометрія ламається у високих вимірах",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-curse-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-distance-concentration.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-contrast-measure.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "nearest-neighbor-search",
          "title": "Пошук найближчого сусіда: точний перебір, індекс і наближена відповідь",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "random-projection",
          "title": "Випадкова проєкція і лема Джонсона — Лінденштрауса",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gjk-collision",
          "title": "Алгоритм GJK: перетин опуклих тіл через множину різниць",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "voronoi-diagram",
          "title": "Діаграма Вороного",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "majority-vote-boyer-moore",
          "title": "Голосування більшості (Бойєр — Мур): переможець за один прохід і фіксовану пам'ять",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "sequence-diff",
          "title": "Порівняння двох послідовностей: найдовша спільна підпослідовність і алгоритми diff",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        }
      ]
    },
    {
      "slug": "numerical-algorithms",
      "title": "Числові",
      "scope": "Арифметика великих чисел, лінійна алгебра, чисельні методи, точні та наближені обчислення.",
      "topics": [
        {
          "slug": "kahan-summation",
          "title": "Компенсоване підсумовування (Кехен)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "newtons-method",
          "title": "Метод Ньютона",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "automatic-differentiation",
          "title": "Автоматичне диференціювання",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "numerical-ode",
          "title": "Числові методи розв'язку ОДУ",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "float-formats",
          "title": "Формати чисел із рухомою комою (IEEE 754)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "symplectic-integrators",
          "title": "Симплектичні інтегратори (Верле, leapfrog)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "karatsuba-multiplication",
          "title": "Множення Карацуби",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        }
      ]
    },
    {
      "slug": "combinatorial-optimization",
      "title": "Оптимізація",
      "scope": "Пошук найкращого розв'язку в дискретних і неперервних просторах: лінійне, цілочисельне програмування, евристики.",
      "topics": [
        { slug: "inlining", title: "Інлайнінг функцій (Function Inlining)", basic: { status: "empty" }, detailed: { status: "pending" } },
        {
          "slug": "hungarian-algorithm",
          "title": "Алгоритм Угорського методу",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "mean-shift",
          "title": "Зсув до середнього",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "simulated-annealing",
          "title": "Імітація відпалу (simulated annealing)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "set-cover",
          "title": "Задача про покриття множини",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "travelling-salesman",
          "title": "Задача комівояжера",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        }
      ]
    },
    {
      "slug": "cryptographic-algorithms",
      "title": "Криптографія",
      "scope": "Шифрування, хеш-функції, цифрові підписи, протоколи обміну ключами.",
      "topics": [
        {
          "slug": "berlekamp-massey",
          "title": "Алгоритм Берлекампа–Мессі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "rsa",
          "title": "RSA",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "miller-rabin",
          "title": "Тест простоти Міллера–Рабіна",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-miller-rabin.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-liar-bound.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-miller-rabin.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "csprng",
          "title": "Криптографічний генератор випадкових чисел (CSPRNG)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-rng-disasters.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-unpredictability.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-fast-key-erasure.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "fermat-primality-test",
          "title": "Тест простоти Ферма",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "block-cipher",
          "title": "Блоковий шифр",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "stream-cipher",
          "title": "Потоковий шифр",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "entropy-source",
          "title": "Джерело ентропії (TRNG)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "montgomery-multiplication",
          "title": "Множення за Монтгомері",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "solovay-strassen",
          "title": "Тест простоти Соловея–Штрассена",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "diffie-hellman",
          "title": "Обмін ключами Діффі — Геллмана",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "keyed-hash-mac",
          "title": "Ключований хеш і код автентичності (MAC)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        }
      ]
    },
    {
      "slug": "data-compression",
      "title": "Стиснення",
      "scope": "Скорочення даних без втрат і з втратами: ентропійне, словникове, трансформаційне кодування.",
      "topics": [
        {
          "slug": "why-compress",
          "title": "Навіщо стискати",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-dct.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "auditory-masking",
          "title": "Психоакустичне маскування",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "jpeg-intra",
          "title": "JPEG",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-jpeg.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-dct.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-jpeg-encode.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-markers.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "inter-frame",
          "title": "Міжкадрове стиснення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-mpeg.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-motion-estimation.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "quality-bitrate",
          "title": "Якість і бітрейт",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-fpv-digital.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "lossless-huffman-lz",
          "title": "Стиснення без втрат",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "entropy",
          "title": "Ентропія",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "huffman-coding",
          "title": "Код Гаффмана",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-huffman-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "rle",
          "title": "RLE (довжини серій)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "arithmetic-coding",
          "title": "Арифметичне кодування",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "shannon-fano",
          "title": "Код Шеннона–Фано",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "lz77",
          "title": "LZ77",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-lz77-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "lzw",
          "title": "LZW",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "deflate",
          "title": "DEFLATE",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-pkzip.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "asymmetric-numeral-systems",
          "title": "ANS: асиметричні системи числення",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "cabac",
          "title": "CABAC",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "rate-distortion",
          "title": "Rate-distortion оптимізація",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "deblocking-filter",
          "title": "Деблокінговий фільтр",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "subpixel-interpolation",
          "title": "Субпіксельна інтерполяція у відео",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "h265-hevc",
          "title": "H.265 / HEVC",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "av1",
          "title": "AV1",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "motion-estimation-search",
          "title": "Пошук руху (motion estimation)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "rate-control-algorithms",
          "title": "Алгоритми керування бітрейтом",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "psnr-ssim",
          "title": "Метрики якості відео: PSNR і SSIM",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "hrd-buffer-model",
          "title": "Модель HRD-буфера відеопотоку",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "run-length-codes",
          "title": "Коди довжин серій (Modified Huffman, MR)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "shannon-fano-elias",
          "title": "Код Шеннона–Фано–Еліаса",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "prefix-codes",
          "title": "Префіксні коди та декодованість",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "cobs-encoding",
          "title": "Кодування COBS",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "crc-algorithm",
          "title": "Алгоритм CRC: таблиця залишків і побітний метод",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "h264-nal-structure",
          "title": "H.264: NAL-одиниці, SPS/PPS і ключові кадри",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-nal-layer.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-nal-parser.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-sps-pps.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "exp-golomb",
          "title": "Експоненційний код Голомба: ue(v) і se(v) у відеостандартах",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "cavlc",
          "title": "CAVLC: контекстно-адаптивні коди змінної довжини",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "h264-profiles-levels",
          "title": "Профілі та рівні H.264",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        }
      ]
    },
    {
      "slug": "machine-learning",
      "title": "Машинне навчання",
      "scope": "Алгоритми, що будують моделі з даних: навчання з учителем і без, ансамблі, нейромережі, навчання з підкріпленням.",
      "topics": [
        {
          "slug": "what-is-ml",
          "title": "Що таке ML",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-ai-winters.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "train-vs-inference",
          "title": "Навчання vs вивід",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "neuron-layer",
          "title": "Нейрон і шар",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "gradient-descent",
          "title": "Градієнтний спуск",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "cnn",
          "title": "Згорткові мережі",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-lecun-cnn.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "overfitting",
          "title": "Перенавчання",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "tinyml",
          "title": "TinyML",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-tinyml-field.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-arena-planner.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-tflm.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "ml-limits-ethics",
          "title": "Межі й етика",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "pending"
          },
          "hist": [
            {
              "file": "hist-shortcut-legends.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-base-rate-threshold.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-slice-audit.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "transfer-learning",
          "title": "Transfer learning (перенесення навчання)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-transferable-features.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "anchor-boxes",
          "title": "Якорі та кодування рамок",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "model-quantization",
          "title": "Квантування нейромереж",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-int8-jacob.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-affine-quant.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-int8-inference.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "backpropagation",
          "title": "Зворотне поширення помилки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-multiple-discovery.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "activation-functions",
          "title": "Функції активації",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-relu-triumph.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-softmax.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "sgd-optimizers",
          "title": "Оптимізатори: SGD, моментум, Adam",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "vanishing-gradient",
          "title": "Затухаючий і вибуховий градієнт",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "weight-initialization",
          "title": "Ініціалізація ваг нейромережі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "perceptron",
          "title": "Перцептрон Розенблатта",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "regularization",
          "title": "Регуляризація",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-regularization.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-l1-sparsity.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "data-augmentation",
          "title": "Аугментація даних",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-alexnet-2012.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-mixup.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "cross-validation",
          "title": "Крос-валідація",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-cross-validation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-kfold-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "bias-variance-tradeoff",
          "title": "Компроміс зміщення й дисперсії",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "knowledge-distillation",
          "title": "Дистиляція знань",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-distillation-lineage.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-distillation-loss.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-distill-mnist-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "weight-pruning",
          "title": "Прорідження мережі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-obd-lottery.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-pruning-saliency.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "loss-functions",
          "title": "Функції втрат у машинному навчанні",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-mse-likelihood.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "supervised-learning",
          "title": "Навчання з учителем",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-nearest-neighbor.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-loss-functions.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "unsupervised-learning",
          "title": "Навчання без учителя",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-kmeans-lineage.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "reinforcement-learning",
          "title": "Навчання з підкріпленням",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-rl-lineage.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "edge-computing",
          "title": "Edge computing",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "companion-computer",
          "title": "Бортовий комп'ютер (companion)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "inference-latency",
          "title": "Латентність інференсу",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-realtime-inference.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "cosine-similarity",
          "title": "Косинусна схожість",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "autoencoder",
          "title": "Автокодер",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-linear-pca.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-autoencoder-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "dbscan",
          "title": "DBSCAN: щільнісна кластеризація",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "pca",
          "title": "Метод головних компонент (PCA)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "variational-autoencoder",
          "title": "Варіаційний автокодер (VAE)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "restricted-boltzmann-machine",
          "title": "Обмежена машина Больцмана (RBM)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "distribution-shift",
          "title": "Зсув розподілу даних",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "confidence-calibration",
          "title": "Калібрування впевненості моделі",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "model-explainability",
          "title": "Пояснюваність моделей",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "fairness-criteria",
          "title": "Критерії справедливості моделі та їхня несумісність",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "intrinsic-dimension",
          "title": "Внутрішня розмірність даних і гіпотеза многовиду",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        }
      ]
    },
    {
      "slug": "computer-vision",
      "title": "Зір",
      "scope": "Аналіз зображень і відео: фільтрація, ознаки, сегментація, відновлення геометрії сцени.",
      "topics": [
        {
          "slug": "bayer-demosaic",
          "title": "Демозаїка",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-bryce-bayer.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-demosaic-bilinear.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "image-as-data",
          "title": "Зображення як дані",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-summer-vision.md",
              "status": "done"
            },
            {
              "file": "hist-maxwell-rgb.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-color-spaces.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-rgb-hsv-convert.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "histogram",
          "title": "Гістограма",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-hurter-driffield.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-equalization.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-histogram-lut.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "convolution-filters",
          "title": "Згортки й фільтри",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-2d-convolution.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-separable-blur.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "edge-detection",
          "title": "Виділення меж",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-sobel-feldman.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-canny-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "threshold-morphology",
          "title": "Пороги й морфологія",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-otsu-derivation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-threshold-morphology-pipeline.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "object-detection",
          "title": "Виявлення об'єктів",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-hough.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-hough.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-color-blob.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "nn-detectors",
          "title": "Нейродетектори",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-neural-nets.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-iou-nms.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-yolo-postprocess.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "tracking",
          "title": "Трекінг",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-tracking-history.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-kf-tracking-state.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-sort-tracker.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "compute-cost",
          "title": "Вартість обчислень",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-apollo-guidance.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "edge-adaptive-demosaic",
          "title": "Крайо-чутлива демозаїка",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "raw-processing-pipeline",
          "title": "Конвеєр обробки RAW",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "roofline-model",
          "title": "Roofline-модель продуктивності",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "quantization-inference",
          "title": "Квантування для інференсу",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "separable-filters",
          "title": "Розділювані фільтри",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "bilateral-filter",
          "title": "Білатеральний фільтр",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "kernel-frequency-response",
          "title": "Частотна характеристика ядер",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "corner-detection",
          "title": "Детектори кутів: Гарріс, Ші–Томасі, FAST",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-corner-lineage.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-second-moment.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "scale-space",
          "title": "Масштабний простір і піраміда Гауса",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "clahe",
          "title": "CLAHE — локальна адаптивна еквалізація",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "tone-curve",
          "title": "Тонова крива й гамма-корекція",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "color-histogram",
          "title": "Колірна гістограма і трекінг за кольором",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "pixel-formats",
          "title": "Формати пікселів і буферів зображення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-chroma-subsampling.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "nms-algorithm",
          "title": "Non-Maximum Suppression",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "detection-architectures",
          "title": "Архітектури детекторів: YOLO, SSD, R-CNN",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "fiducial-markers",
          "title": "Фідуційні мітки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "background-subtraction",
          "title": "Відрахування фону",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "feature-matching",
          "title": "Зіставлення ключових точок",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-sift-to-orb.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-descriptor-distance.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-orb-match-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "otsu-method",
          "title": "Метод Оцу",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "adaptive-thresholding",
          "title": "Адаптивний поріг",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "hit-or-miss",
          "title": "Перетворення влучання-промаху",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "watershed-segmentation",
          "title": "Сегментація водорозділом",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "optical-flow",
          "title": "Оптичний потік",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-two-schools.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-optical-flow-constraint.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "data-association",
          "title": "Прив'язка даних",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "white-balance",
          "title": "Баланс білого",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-color-constancy.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-von-kries-diagonal.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-auto-white-balance.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "color-filter-array-variants",
          "title": "Альтернативні матриці кольорових фільтрів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "frequency-filtering",
          "title": "Частотна фільтрація зображень",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "marr-hildreth-log",
          "title": "Оператор Марра–Гілдрет (LoG)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "hough-transform",
          "title": "Перетворення Хафа",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "nn-segmentation",
          "title": "Сегментація зображень нейромережею",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "aruco-apriltag",
          "title": "Фідуційні мітки ArUco та AprilTag",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-fiducial-lineage.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-aruco-decode.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "blob-analysis",
          "title": "Аналіз плям",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "template-matching",
          "title": "Зіставлення з шаблоном",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "detection-metrics",
          "title": "Метрики детектора",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "multi-object-tracking",
          "title": "Трекінг багатьох цілей",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "depthwise-separable-conv",
          "title": "Розділювана за глибиною згортка",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "stereo-vision",
          "title": "Стереозір",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "tile-rendering",
          "title": "Тайловий рендеринг",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "alpha-blending",
          "title": "Альфа-змішування",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "pose-estimation",
          "title": "Відновлення пози за точками (PnP)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-pnp-lineage.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-p3p-cosines.md",
              "status": "done"
            },
            {
              "file": "math-reprojection-jacobian.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-pnp-solver.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "camera-model",
          "title": "Модель камери-обскури й внутрішні параметри",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "camera-calibration",
          "title": "Калібрування камери",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "homography",
          "title": "Гомографія: перетворення площини в площину",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "bundle-adjustment",
          "title": "Оптимізація пучком (bundle adjustment)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "absolute-orientation",
          "title": "Абсолютна орієнтація (суміщення двох наборів точок)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "image-georeferencing",
          "title": "Геоприв'язка аерознімка: від пози камери до координат на землі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-pixel-to-ground.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-georef-error.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-direct-georeferencing.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "orthorectification",
          "title": "Ортотрансформування знімка",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "ground-control-points",
          "title": "Опорні точки на місцевості (GCP)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        }
      ]
    },
    {
      "slug": "signal-robotics",
      "title": "Сигнали",
      "scope": "Цифрова обробка сигналів (спектр, фільтрація, дискретизація) разом із плануванням руху, локалізацією та керуванням автономних агентів.",
      "topics": [
        {
          "slug": "signal-noise",
          "title": "Шум у сигналі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-snr.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "moving-average",
          "title": "Ковзне середнє",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "median-filter",
          "title": "Медіанний фільтр",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "ema",
          "title": "EMA",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-ema-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "smoothing-vs-lag",
          "title": "Згладжування й затримка",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "fft",
          "title": "ШПФ",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-fft.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "filter-as-spectrum-shaper",
          "title": "Формувач спектра",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "fir-filter",
          "title": "КІХ-фільтр",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-fir-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "iir-filter",
          "title": "БІХ-фільтр",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-biquad-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "band-filters",
          "title": "Смугові фільтри",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-type-transformations.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "fixed-point-implementation",
          "title": "Реалізація fixed-point",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "sensor-fusion",
          "title": "Поєднання давачів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "complementary-filter",
          "title": "Комплементарний фільтр",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-complementary-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "kalman-filter",
          "title": "Фільтр Калмана",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-kalman.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "discrete-pid",
          "title": "Дискретний ПІД",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-pid-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "sensor-insufficiency",
          "title": "Недостатність давача",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-draper.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "motion-model",
          "title": "Модель руху",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-cv-ca-models.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "predict-vs-measure",
          "title": "Передбачення vs вимір",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-recursive-estimation.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-optimal-fusion.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-predict-correct-tracker.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "kalman-ekf",
          "title": "Розширений фільтр Калмана (EKF)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-fusion-in-flight.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "latency-sync",
          "title": "Затримки й синхро",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "odometry",
          "title": "Одометрія",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "motion-profiles",
          "title": "Профілі руху",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "roll-pitch-yaw-control",
          "title": "Керування roll/pitch/yaw",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "motor-mixer",
          "title": "Мікшер",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "instability-stabilization",
          "title": "Потреба стабілізації",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "stabilization-cascade",
          "title": "Каскад стабілізації",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "missions-waypoints",
          "title": "Місії й точки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "sense-decide-act-loop",
          "title": "Контур offboard",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "one-stack-many-bodies",
          "title": "Один стек",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "rover-steering",
          "title": "Ровер",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-ackermann.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-pure-pursuit.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "boat-underwater",
          "title": "Човен і підводний",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-acoustic-positioning.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-depth-hold-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "pure-pursuit-navigation",
          "title": "Навігація pure pursuit",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-pursuit-geometry.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-pursuit-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "platform-selection",
          "title": "Вибір платформи",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "mission-planning-map",
          "title": "Планування на карті",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "closing-the-loop",
          "title": "Замкнути контур",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "where-next",
          "title": "Куди далі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "jitter-buffer",
          "title": "Буфер джитера",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "adaptive-filter",
          "title": "Адаптивний фільтр",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "shelf-filter",
          "title": "Поличковий фільтр",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "all-pass-filter",
          "title": "Всепропускний фільтр",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "double-ema",
          "title": "Подвійне EMA (DEMA) — компенсація тренду",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "adaptive-ema",
          "title": "Адаптивне EMA — змінний коефіцієнт згладжування",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "goertzel",
          "title": "Алгоритм Гертцеля",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "parks-mcclellan",
          "title": "Алгоритм Parks-McClellan",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "polyphase-fir",
          "title": "Поліфазний КІХ і мультирейт",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "filter-order-estimation",
          "title": "Оцінка порядку фільтра",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "limit-cycles-iir",
          "title": "Граничні цикли у БІХ-фільтрах",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "bilinear-transform",
          "title": "Білінійне перетворення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "butterworth-filter",
          "title": "Фільтр Баттерворта",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "chebyshev-filter",
          "title": "Фільтр Чебишева",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "direct-form-iir",
          "title": "Форми реалізації БІХ (Direct Form)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "packet-loss-concealment",
          "title": "Приховування втрат пакетів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "audio-time-scaling",
          "title": "Зміна темпу без зміни висоти тону",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-time-scaling.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-wsola-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "unscented-kalman-filter",
          "title": "Несцентований фільтр Калмана (UKF)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "particle-filter",
          "title": "Фільтр частинок",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "innovation-gating",
          "title": "Ворота несподіванки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "sensor-timestamp-sync",
          "title": "Синхронізація міток часу давачів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "trimmed-mean",
          "title": "Усічене середнє",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "ctrv-motion-model",
          "title": "Модель CTRV: стала кутова швидкість і швидкість",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "imm-filter",
          "title": "Фільтр IMM (взаємодіючі мультимоделі)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "bicycle-kinematic-model",
          "title": "Кінематична велосипедна модель",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "actuator-allocation",
          "title": "Розподіл керування по приводах",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "weighted-moving-average",
          "title": "Зважене ковзне середнє",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "cumulative-moving-average",
          "title": "Кумулятивне ковзне середнє",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "innovation-gate",
          "title": "Брама нової інформації (innovation gate)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "quaternion-attitude-control",
          "title": "Кватерніонне керування орієнтацією",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-hamilton.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-half-angle.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-error-quaternion-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "rate-angle-cascade",
          "title": "Каскадний регулятор: кут і кутова швидкість",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "ahrs",
          "title": "AHRS — система відліку орієнтації й курсу",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "madgwick-mahony",
          "title": "Алгоритми Madgwick і Mahony",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "visual-inertial-odometry",
          "title": "Візуально-інерціальна одометрія",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-msckf.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "causal-filter",
          "title": "Причинний фільтр і групова затримка",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "three-loop-cascade",
          "title": "Трирівневий каскад (положення–швидкість–струм)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "real-time-systems",
          "title": "Системи реального часу",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "dead-reckoning",
          "title": "Інерціальне числення позиції",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "phase-margin",
          "title": "Запас по фазі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "bumpless-transfer",
          "title": "Безударне перемикання регулятора",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "goertzel-algorithm",
          "title": "Алгоритм Герцеля",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "overlap-add",
          "title": "Overlap-add і потоковий спектр",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "dithering",
          "title": "Дізеринг",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "geofence-algorithm",
          "title": "Алгоритм геозони",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "rfid-anticollision",
          "title": "Антиколізія RFID: кілька міток в одному полі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "rtk-integer-ambiguity",
          "title": "Розв'язання цілочислової неоднозначності RTK",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-lambda.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-double-difference.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "digital-filters",
          "title": "Цифрові фільтри",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "acceleration-profile",
          "title": "Профілі розгону привода",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "cycle-counting-palmgren-miner",
          "title": "Rainflow і правило Майнера",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "welford-online",
          "title": "Онлайн-алгоритм Велфорда",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "pole-zero-plot",
          "title": "Площина полюсів-нулів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "cic-filter",
          "title": "CIC-фільтр (каскад інтегратор–гребінка)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "survey-grid-coverage",
          "title": "Покриття полігону галсами: планування зйомки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-min-width.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-boustrophedon.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-coverage-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "plot-downsampling",
          "title": "Прорідження часового ряду для екрана: огинаюча замість кожного відліку",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "configuration-space",
          "title": "Конфігураційний простір: рух тіла як рух точки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        }
      ]
    },
    {
      "slug": "parallel-distributed",
      "title": "Паралельні",
      "scope": "Одночасне виконання на багатьох процесорах зі спільною пам'яттю та системи незалежних вузлів з обміном повідомленнями: примітиви, синхронізація, консенсус, відмовостійкість.",
      "topics": [
        {
          "slug": "gesture-recognition",
          "title": "Розпізнавання жестів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "edf-scheduling",
          "title": "EDF-планування",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "monitor-sync",
          "title": "Монітори й умовні змінні",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "amdahls-law",
          "title": "Закон Амдала",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "lamport-clocks",
          "title": "Чому wall-clock бреше (дрейф, NTP-стрибки) і **годинник Лампорта**",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "vector-clocks",
          "title": "Векторні годинники й обходи розбіжності",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "consensus-problem",
          "title": "Задача консенсусу і чому вона важка (FLP оглядово); коли потрібен консенсус, а коли ні (дорого)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "raft",
          "title": "Raft",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "two-phase-commit",
          "title": "Двофазний коміт і його страх",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "crdt",
          "title": "Безконфліктні типи даних (CRDT)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-crdt.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-convergence.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-or-set.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "operational-transformation",
          "title": "Операційні перетворення (OT)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "two-generals-problem",
          "title": "Задача двох генералів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "seqlock",
          "title": "Seqlock: узгоджене читання без блокування читача",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "work-span-model",
          "title": "Робота і глибина: критичний шлях як межа паралельності",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        }
      ]
    }
  ]
}
);
