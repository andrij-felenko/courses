window.__BOOKS__ = window.__BOOKS__ || [];
window.__BOOKS__.push(
{
  "type": "book",
  "slug": "math",
  "title": "Математика",
  "sections": [
    {
      "slug": "logic-foundations",
      "title": "Логіка",
      "scope": "Формальні системи, доведення, обчислюваність і самі підвалини математики, включно з теорією множин.",
      "topics": [
        {
          "slug": "truth-tables",
          "title": "Таблиці істинності та логічні зв'язки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-truth-tables.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-boolean-eval.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-truth-table-generator.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "propositional-logic",
          "title": "Числення висловлювань (пропозиційна логіка)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-propositional-logic.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-deduction-theorem.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-sat-dpll-solver.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "first-order-logic",
          "title": "Логіка першого порядку (предикати та квантори)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-first-order-logic.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-prenex-skolem.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-first-order-unifier.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "proof-systems-gentzen",
          "title": "Системи дедукції: секвенційне числення Ґентцена та системи Гільберта",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-gentzen-proof-theory.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-cut-elimination-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-sequent-calculus-prover.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "resolution-principle",
          "title": "Принцип резолюцій та автоматичне доведення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-robinson-resolution.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-refutation-completeness.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-resolution-prover.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "model-theory-basics",
          "title": "Теорія моделей: інтерпретації та теорема Левенгейма–Сколема",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-lowenheim-skolem.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-skolem-paradox.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-model-evaluator.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "intuitionistic-logic",
          "title": "Інтуїціоністська (конструктивна) логіка та семантика Кріпке",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-brouwer-intuitionism.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-kripke-frames.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-kripke-evaluator.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "type-theory-lambda",
          "title": "Просто типізоване лямбда-числення та теорія типів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-church-stlc.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-curry-howard.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-type-checker.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "boolean-algebra",
          "title": "Булева алгебра",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-boole.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-axioms-proofs.md",
              "status": "done"
            }
          ],
          "comp": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "karnaugh-maps",
          "title": "Карти Карно",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "proj": [
            {
              "file": "proj-quine-mccluskey.md",
              "status": "done"
            }
          ],
          "hist": [],
          "comp": [],
          "math": [],
          "api": []
        },
        {
          "slug": "finite-automata",
          "title": "Скінченні автомати",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "shannon-expansion",
          "title": "Теорема Шеннона про розкладання",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-boole-shannon.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-cofactors.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-recursive-expansion.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "logic-minimization",
          "title": "Мінімізація логічних функцій",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-minimization.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-prime-implicants.md",
              "status": "done"
            }
          ],
          "comp": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "regular-languages",
          "title": "Регулярні мови",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-chomsky-hierarchy.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-pumping-lemma.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-product-construction.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "pushdown-automata",
          "title": "Магазинні автомати",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-pushdown-store.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-pda-cfg-equivalence.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-expression-parser.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "turing-machine",
          "title": "Машина Тюринга",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-computable-numbers.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-turing-simulator.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "api": []
        },
        {
          "slug": "karnaugh-map",
          "title": "Карта Карно і мінімізація схем",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-quine-mccluskey.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-prime-implicants.md",
              "status": "done"
            }
          ],
          "comp": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "functional-completeness",
          "title": "Функціональна повнота",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-post.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-post-criterion.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-completeness-check.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "mathematical-induction",
          "title": "Математична індукція",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-induction-history.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-code-correctness.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "api": []
        },
        {
          "slug": "mathematical-proof",
          "title": "Математичне доведення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-birth-of-proof.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-proof-methods.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-proof-checker.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "natural-numbers",
          "title": "Натуральні числа",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-peano-axioms.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-recursive-arithmetic.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-peano-numbers.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "well-ordering-principle",
          "title": "Принцип повного впорядкування",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-zermelo.md",
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
              "file": "proj-termination.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "infinite-descent",
          "title": "Нескінченний спуск Ферма",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-fermat-descent.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-right-triangle-area.md",
              "status": "done"
            },
            {
              "file": "math-two-squares-descent.md",
              "status": "done"
            }
          ],
          "comp": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "formal-language",
          "title": "Формальна мова",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-thue-to-backus.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-how-many-languages.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-language-algebra.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "chomsky-hierarchy",
          "title": "Ієрархія Хомського",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "math": [
            {
              "file": "math-strict-inclusions.md",
              "status": "done"
            }
          ],
          "hist": [],
          "comp": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "zhegalkin-polynomial",
          "title": "Поліном Жегалкіна",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-arithmetization.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-mobius-transform.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-anf-transform.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "binary-decision-diagram",
          "title": "Двійкова діаграма рішень (BDD)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "math": [
            {
              "file": "math-canonicity.md",
              "status": "done"
            }
          ],
          "hist": [],
          "comp": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "boolean-satisfiability",
          "title": "Задача здійсненності (SAT)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-cook-levin.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-reductions.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-dpll-solver.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "godel-incompleteness",
          "title": "Теореми Геделя про неповноту",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-hilbert-program.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-godel-numbering.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-self-reference-code.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "church-turing-thesis",
          "title": "Теза Черча–Тюринга",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-thesis-birth.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-three-models.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "api": []
        },
        {
          "slug": "busy-beaver",
          "title": "Завзятий бобер (busy beaver)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-beaver-hunt.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-uncomputable.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-beaver-search.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "set-theory",
          "title": "Теорія множин",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-cantor.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-everything-is-a-set.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-sets-in-code.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "axiom-of-choice",
          "title": "Аксіома вибору",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "math": [
            {
              "file": "math-nonmeasurable.md",
              "status": "done"
            },
            {
              "file": "math-zorn-equivalence.md",
              "status": "done"
            }
          ],
          "hist": [],
          "comp": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "ordinal-numbers",
          "title": "Порядкові числа (ординали)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-cantor-ordinals.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-ordinal-arithmetic.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-goodstein.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "proof-by-contradiction",
          "title": "Доведення від супротивного",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-pythagoras-sqrt2.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "countable-sets",
          "title": "Зліченні та незліченні множини",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-cantor-infinity.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "linear-bounded-automaton",
          "title": "Лінійно обмежений автомат",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-myhill-lba.md",
              "status": "done"
            }
          ],
          "proj": [],
          "api": [
            {
              "file": "api-chomsky-hierarchy.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": []
        },
        {
          "slug": "decidable-languages",
          "title": "Розв'язні мови",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-halting-problem.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "proj": [
            {
              "file": "proj-turing-decider-sim.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-decidability-classes.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "russell-paradox",
          "title": "Парадокс Рассела",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-frege-letter.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "cantor-diagonal",
          "title": "Діагональний метод Кантора",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-cantor-1891-paper.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "tarski-undefinability",
          "title": "Теорема Тарського про невизначність істини",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-tarski-1936-paper.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "zfc-set-theory",
          "title": "Аксіоматика Цермело-Френкеля (ZFC)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-zermelo-fraenkel-1908.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "lambda-calculus",
          "title": "Лямбда-числення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-church-1936-lambda.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "general-recursive-functions",
          "title": "Загальнорекурсивні функції",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-godel-kleene-1936.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "primitive-recursive-functions",
          "title": "Примітивно-рекурсивні функції",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-birth-of-recursion.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-diagonal-not-pr.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-primrec-interpreter.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "kleene-recursion-theorem",
          "title": "Теорема рекурсії Кліні",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "cardinal-numbers",
          "title": "Кардинальні числа (потужність)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "continuum-hypothesis",
          "title": "Гіпотеза континууму",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-cantor-cohen.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-cohen-forcing.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-forcing-simulator.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "equivalence-relation",
          "title": "Відношення еквівалентності",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-equivalence-concept.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-quotient-sets.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-equivalence-partitioner.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "rice-theorem",
          "title": "Теорема Райса",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-henry-rice.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-rice-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-rice-analyzer.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "ackermann-function",
          "title": "Функція Аккермана",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-wilhelm-ackermann.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-hyperoperators.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-ackermann-memoizer.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "skolem-paradox",
          "title": "Парадокс Сколема",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-skolem-1922.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-skolemization.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-skolem-relativizer.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "kripke-semantics",
          "title": "Семантика та фрейми Кріпке",
          "status": "done",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-saul-kripke.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-modal-correspondence.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-kripke-model-checker.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "curry-howard-isomorphism",
          "title": "Ізоморфізм Каррі — Говарда",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-curry-howard.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-dependent-types.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-proof-assistant-mini.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "cohen-forcing",
          "title": "Метод форсингу Коена",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-paul-cohen.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-generic-filters.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-forcing-conditions.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "quotient-sets",
          "title": "Фактор-множини",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-dedekind-quotient.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-canonical-projection.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-quotient-builder.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "hyperoperators",
          "title": "Гіпероператори та тетрація",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-goodstein-knuth.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-tetration-properties.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-hyperoperator-evaluator.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "primes",
          "title": "primes",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "empty"
          }
        },
        {
          "slug": "logarithm",
          "title": "logarithm",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "empty"
          }
        },
        {
          "slug": "series",
          "title": "series",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "empty"
          }
        },
        {
          "slug": "number-theory",
          "title": "number theory",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "empty"
          }
        },
        {
          "slug": "geometry",
          "title": "geometry",
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
      "slug": "number-theory",
      "title": "Теорія чисел",
      "scope": "Властивості цілих чисел, подільність, прості числа, діофантові рівняння та арифметичні структури.",
      "topics": [
        {
          "slug": "why-binary",
          "title": "Чому двійкова",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-leibniz.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "positional-systems",
          "title": "Позиційні системи",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-hex-notation.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "twos-complement",
          "title": "Доповняльний код",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-modular-arithmetic.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-modular-arithmetic.md",
              "status": "done"
            }
          ],
          "comp": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "modular-arithmetic",
          "title": "Модульна арифметика",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "address-space",
          "title": "Адресний простір",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "twos-complement-arithmetic",
          "title": "Арифметика доповняльного коду",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-method-of-complements.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-overflow-detection.md",
              "status": "done"
            }
          ],
          "comp": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "binary-logarithm",
          "title": "Двійковий логарифм",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-binary-logarithm.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-change-of-base.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-ilog2.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "gcd-euclidean",
          "title": "НСД і алгоритм Евкліда",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-euclid-algorithm.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-bezout.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-gcd-code.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "chinese-remainder-theorem",
          "title": "Китайська теорема про залишки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-sunzi-to-gauss.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-crt-derivation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-crt-solver.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "euler-totient",
          "title": "Функція Ейлера і теорема Ейлера",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-euler-fermat.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-euler-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-rsa-toy.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "floating-point",
          "title": "Числа з рухомою комою",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-birth-of-floating-point.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-representable-set.md",
              "status": "done"
            }
          ],
          "comp": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "bcd",
          "title": "BCD — двійково-десятковий код",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-bcd-computing.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-bcd-arithmetic.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-bcd-adder.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "octal-system",
          "title": "Вісімкова система та Unix-права",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-octal-pdp.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-radix-conversion.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-chmod-parser.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "ones-complement",
          "title": "Обернений код",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-ones-complement-arch.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-ones-complement-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-internet-checksum.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "sign-magnitude",
          "title": "Знак-величина",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-ibm-7090.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-sign-magnitude-algebra.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-float-sign-bits.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "ternary-computing",
          "title": "Трійкова основа та комп'ютер Сетунь",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-setun-computer.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-radix-economy.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-balanced-ternary-ALU.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "binary-arithmetic",
          "title": "Арифметика в двійковій системі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-binary-logic-gates.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-carry-lookahead.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-binary-alu-simulator.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "binary-fractions",
          "title": "Двійкові дроби та точність представлення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-floating-point-crisis.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-period-length.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-fixed-point-class.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "signed-multiplication",
          "title": "Знакове множення: алгоритм Бута",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-andrew-booth.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-booth-reencoding.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-booth-multiplier-sim.md",
              "status": "done"
            },
            {
              "file": "proj-booth-radix4-sim.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "prime-numbers",
          "title": "Прості числа",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-eratosthenes-euclid.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-prime-distribution.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-segmented-sieve.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "fundamental-theorem-arithmetic",
          "title": "Основна теорема арифметики",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-gauss-disquisitiones.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-euclid-lemma.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-prime-factorizer.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "lcm",
          "title": "НСК — найменше спільне кратне",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-lcm-fractions.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-lcm-lattice.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-lcm-calculator.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "linear-diophantine",
          "title": "Лінійні діофантові рівняння",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-diophantus.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-nonnegative-solutions.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-diophantine-solver.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "modular-inverse",
          "title": "Обернений елемент за модулем",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-modulo-arithmetic.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-ring-units.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-modular-inverse.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "modular-exponentiation",
          "title": "Піднесення до степеня за модулем",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-diffie-hellman.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-square-and-multiply.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-modexp-fast.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "fermat-little-theorem",
          "title": "Мала теорема Ферма",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-fermat-1640.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-more-proofs.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-fermat-test.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "multiplicative-order",
          "title": "Мультиплікативний порядок",
          "basic": {
            "status": "done"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-euler-totient.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-order-divisibility.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-order-calculator.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "carmichael-function",
          "title": "Функція Кармайкла λ(n)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-carmichael.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-lambda-derivation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-lambda.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "fibonacci-numbers",
          "title": "Числа Фібоначчі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-fibonacci.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-identities.md",
              "status": "done"
            },
            {
              "file": "math-zeckendorf.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-fast-fibonacci.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "continued-fractions",
          "title": "Ланцюгові дроби",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-convergents.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-best-approximation.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "perfect-numbers",
          "title": "Досконалі числа",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-perfect-numbers.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-euler-converse.md",
              "status": "done"
            },
            {
              "file": "math-odd-perfect.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-finding-perfect.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "mersenne-primes",
          "title": "Числа Мерсенна і прості Мерсенна",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-mersenne-hunt.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-divisor-form.md",
              "status": "done"
            },
            {
              "file": "math-euclid-euler.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-lucas-lehmer.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "irrational-numbers",
          "title": "Ірраціональні числа",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-hippasus-irrationality.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-continued-fractions.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-continued-fraction-sim.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "pythagorean-triples",
          "title": "Трійки Піфагора",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-plimpton.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-rational-points.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-generate-triples.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "fermats-last-theorem",
          "title": "Велика теорема Ферма",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-margin-to-wiles.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-descent-n4.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-search-and-near-misses.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "quadratic-residue",
          "title": "Квадратичні лишки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-golden-theorem.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-reciprocity-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-jacobi-symbol.md",
              "status": "done"
            },
            {
              "file": "proj-modular-sqrt.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "hash-and-digital-signature",
          "title": "Хеш і цифровий підпис",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "primitive-roots",
          "title": "Первісні корені та циклічність групи лишків",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-gauss-primitive-root.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-discrete-log-hardness.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-primitive-root-finder.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "frobenius-number",
          "title": "Число Фробеніуса (задача про монети)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-frobenius-sylvester.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-sylvester-formula.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-frobenius-solver.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "primitive-root",
          "title": "Первісний корінь",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "carmichael-numbers",
          "title": "Числа Кармайкла",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-carmichael-discovery.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-korselt-criterion.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-miller-rabin-test.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "lucas-numbers",
          "title": "Числа Люка",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "pell-equation",
          "title": "Рівняння Пелля",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "triangular-numbers",
          "title": "Трикутні числа",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "amicable-numbers",
          "title": "Дружні числа",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "abundant-deficient-numbers",
          "title": "Надлишкові й недостатні числа",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "sum-of-two-squares",
          "title": "Сума двох квадратів (теорема Ферма)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "germain-primes",
          "title": "Прості числа Софі Жермен",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "golden-ratio",
          "title": "Золотий перетин",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "elliptic-curves",
          "title": "Еліптичні криві",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "modular-forms",
          "title": "Модулярні форми",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "floor-division",
          "title": "Цілочислове ділення й підлога",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "fractions",
          "title": "Звичайні дроби",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "negative-numbers",
          "title": "Від'ємні числа",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "equidistribution",
          "title": "Рівномірний розподіл за модулем одиниці",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "radix-conversion",
          "title": "Перетворення позиційних систем числення",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-radix-history.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-horner-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-universal-radix-converter.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "radix-economy",
          "title": "Економічність основи системи числення",
          "status": "done",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-shannon-radix.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-radix-optimum-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-radix-economy-sim.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "carry-lookahead-adder",
          "title": "Прискорені суматори з паралельним переносом",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-weinberger-smith.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-prefix-tree.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-cla-4bit-simulator.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "binary-period-length",
          "title": "Періодичність раціональних двійкових дробів",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-gauss-repeating-decimals.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-ord-period-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-period-analyzer.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "booth-algorithm",
          "title": "Алгоритм та рекодування Бута",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-andrew-booth-arc.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-booth-algebraic-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-booth-radix4-sim.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "prime-distribution",
          "title": "Розподіл простих чисел та Дзета-функція",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-riemann-1859.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-euler-product-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-pi-x-estimator.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "euclidean-lemma",
          "title": "Лема Евкліда",
          "status": "done",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-euclid-book7.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-bezout-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-euclid-lemma-checker.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "divisor-lattice",
          "title": "Решітка дільників",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-hasse-lattice.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-boolean-sublattices.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-hasse-generator.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "multiplicative-group-zn",
          "title": "Група оборотних елементів кільця лишків",
          "status": "done",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-euler-gauss-groups.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-chinese-remainder-group.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-group-zn-analyzer.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "square-and-multiply",
          "title": "Алгоритм швидкого піднесення до степеня (Square-and-Multiply)",
          "status": "done",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-pingala-pow.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-side-channel-protection.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-fast-pow-mod.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "discrete-logarithm",
          "title": "Дискретний логарифм та його складність",
          "status": "done",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-diffie-hellman-1976.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-shanks-bsgs-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-bsgs-solver.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "sylvester-frobenius-formula",
          "title": "Формула Сильвестра для числа Фробеніуса",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-sylvester-1884.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-sylvester-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-frobenius-grid-solver.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "korselt-criterion",
          "title": "Критерій Корсельта для чисел Кармайкла",
          "status": "done",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-korselt-1899.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-korselt-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-korselt-checker.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "miller-rabin-test",
          "title": "Тест простоти Міллера — Рабіна",
          "status": "done",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-miller-rabin-1980.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-strong-pseudo-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-miller-rabin-sim.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "bezout-identity",
          "title": "Тотожність Безу та розширений алгоритм Евкліда",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-etienne-bezout.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-extended-gcd-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-ext-gcd-solver.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "euclid-euler-theorem",
          "title": "Теорема Евкліда — Ейлера про досконалі числа",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-perfect-numbers.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-sigma-multiplicative-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-perfect-number-generator.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "euler-product-formula",
          "title": "Тотожність та добуток Ейлера для Дзета-функції",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-euler-1737.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-analytic-continuation-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-zeta-product-sim.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "montgomery-ladder",
          "title": "Сходи Монтгомері та алгоритми константного часу",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-peter-montgomery.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-ladder-invariant-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-montgomery-ladder-sim.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "quadratic-reciprocity",
          "title": "Закон квадратичної взаємності Ґаусса",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [
            {
              "file": "proj-legendre-jacobi-calculator.md",
              "status": "done"
            }
          ],
          "api": []
        },
        {
          "slug": "chord-method-triples",
          "title": "Метод хорди для раціональних точок та Піфагорових трійок",
          "status": "empty",
          "levels": [
            "detailed"
          ],
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-diophantus-chord.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-rational-param-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-pythagorean-generator.md",
              "status": "done"
            }
          ],
          "api": []
        }
      ]
    },
    {
      "slug": "algebra",
      "title": "Алгебра",
      "scope": "Абстрактні алгебраїчні структури — групи, кільця, поля, модулі — та поліноміальні рівняння.",
      "topics": [
        {
          "slug": "rearranging-formulas",
          "title": "Перестановка формул",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-al-jabr.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-worked-rearrangements.md",
              "status": "done"
            }
          ],
          "comp": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "crc",
          "title": "Циклічна надмірність",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "galois-field",
          "title": "Скінченні поля (поля Галуа)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "finite-fields",
          "title": "Скінченні поля",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "polynomial-rings",
          "title": "Кільця многочленів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "lie-group-so3",
          "title": "Група SO(3) і її подвійне покриття SU(2)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "rotation-group-so3",
          "title": "Група SO(3)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "group-theory",
          "title": "Групи, підгрупи й теорема Лагранжа",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-group-concept.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-lagrange-converse.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-group-computation.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "rings",
          "title": "Кільця: додавання й множення в одній структурі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-ring-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-consequences.md",
              "status": "done"
            },
            {
              "file": "math-znz-structure.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-modular-ring.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "monoid",
          "title": "Моноїд",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "semilattice",
          "title": "Напіврешітка",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "field",
          "title": "Поле",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "integral-domain",
          "title": "Область цілісності",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "ideal",
          "title": "Ідеали та фактор-кільця",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "normal-subgroup",
          "title": "Нормальні підгрупи й фактор-групи",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "group-isomorphism",
          "title": "Ізоморфізм груп",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "cauchy-theorem",
          "title": "Теорема Коші (теорія груп)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "sylow-theorems",
          "title": "Теореми Силова",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "computational-group-theory",
          "title": "Обчислювальна теорія груп",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "inverse-operations",
          "title": "Обернені дії",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "quadratic-equations",
          "title": "Квадратні рівняння",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "complete-lattice",
          "title": "Повна ґратка й теорема Кнастера–Тарського",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "semiring",
          "title": "Напівкільце: додавання без віднімання",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "quartic-equation",
          "title": "Рівняння четвертого степеня й розв'язок Феррарі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "partial-fractions",
          "title": "Розклад на прості дроби",
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
      "slug": "linear-algebra",
      "title": "Лінійна алгебра",
      "scope": "Векторні простори, лінійні відображення, матриці та спектральна теорія.",
      "topics": [
        {
          "slug": "superposition",
          "title": "Суперпозиція",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "kronecker-product",
          "title": "Добуток Кронекера",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "linear-systems",
          "title": "Лінійні системи",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "gauss-elimination",
          "title": "Метод Гаусса",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "matrices-as-operations",
          "title": "Матриці як дії",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "rotation-matrices",
          "title": "Матриці повороту",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "vector-components",
          "title": "Складові вектора",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-vector-concept.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "vector-addition",
          "title": "Додавання векторів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "dot-product",
          "title": "Скалярний добуток",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "cross-product",
          "title": "Векторний добуток",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "state-space-representation",
          "title": "Простір станів: опис динамічних систем",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "state-transition-matrix",
          "title": "Матриця переходу стану",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "exterior-product",
          "title": "Зовнішній добуток (форма Грассмана)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "vector-norm",
          "title": "Норма вектора й нормування",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "inner-product-space",
          "title": "Простір зі скалярним добутком",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "lu-decomposition",
          "title": "LU-розклад",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "matrix-condition-number",
          "title": "Умовне число матриці",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gaussian-jordan-elimination",
          "title": "Метод Гаусса–Жордана",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "matrix-rank",
          "title": "Ранг матриці",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "null-space",
          "title": "Ядро лінійного відображення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "matrix-determinant",
          "title": "Визначник матриці",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "eigenvalues",
          "title": "Власні вектори та власні значення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "affine-transform",
          "title": "Афінні перетворення та однорідні координати",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gram-schmidt",
          "title": "Процес Грама–Шмідта та ортогоналізація",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "homogeneous-transform",
          "title": "Однорідні перетворення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "linear-map",
          "title": "Лінійне відображення і матриця",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "linear-combination",
          "title": "Лінійна комбінація векторів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "vector-space",
          "title": "Векторний простір",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "change-of-basis",
          "title": "Зміна базису",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "curvilinear-coordinates",
          "title": "Криволінійні координати і локальний базис",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "svd",
          "title": "Сингулярний розклад (SVD)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "jacobian-matrix",
          "title": "Якобіан: локальне лінійне наближення відображення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-functional-determinants.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-volume-scale.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-numerical-jacobian.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        }
      ]
    },
    {
      "slug": "combinatorics",
      "title": "Комбінаторика",
      "scope": "Підрахунок, перелік і структура скінченних та дискретних конфігурацій, графи.",
      "topics": [
        {
          "slug": "graph-theory",
          "title": "Теорія графів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "graph-coloring",
          "title": "Розфарбування графів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "spanning-tree",
          "title": "Кістякове дерево",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "bipartite-graph",
          "title": "Дводольний граф",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "unsigned-arithmetic",
          "title": "Беззнакова арифметика і переповнення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "formal-grammar",
          "title": "Формальні граматики (CFG, BNF)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "combinations",
          "title": "Комбінації і біноміальний коефіцієнт",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "inclusion-exclusion",
          "title": "Принцип включення-виключення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-surjections.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-subset-sieve.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "de-bruijn-sequence",
          "title": "Послідовності де Брейна",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-de-bruijn.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-counting.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-construct.md",
              "status": "done"
            },
            {
              "file": "proj-debruijn-ctz.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "linear-recurrence",
          "title": "Лінійні рекурентні співвідношення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "permutations",
          "title": "Перестановки",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "lyndon-word",
          "title": "Слова Ліндона",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "stirling-numbers-second-kind",
          "title": "Числа Стірлінга другого роду",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "matrix-tree-theorem",
          "title": "Матрична теорема про дерева (теорема Кірхгофа)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        }
      ]
    },
    {
      "slug": "geometry",
      "title": "Геометрія",
      "scope": "Фігури, простори, відстані й симетрії — від евклідової до проєктивної та алгебраїчної геометрії; включає диференціальну геометрію: гладкі многовиди, кривизну, зв'язності.",
      "topics": [
        {
          "slug": "euler-angles",
          "title": "Кути Ейлера",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-governor-pid.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "quaternions",
          "title": "Кватерніони",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "sine-cosine",
          "title": "Синус і косинус",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "phase-shift",
          "title": "Фаза й зсув",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "power-triangle",
          "title": "Трикутник потужності",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "trilateration",
          "title": "Трилатерація",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gimbal",
          "title": "Кардановий підвіс",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "direction-cosine-matrix",
          "title": "Матриця напрямних косинусів (DCM)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gimbal-lock",
          "title": "Складання рамок (gimbal lock)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "rodrigues-rotation",
          "title": "Формула повороту Родриґа",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "tangent-cotangent",
          "title": "Тангенс і котангенс",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "inverse-trig",
          "title": "Обернені тригонометричні функції",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "trig-identities",
          "title": "Тригонометричні тотожності",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "pythagorean-theorem",
          "title": "Теорема Піфагора",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "surface-normal",
          "title": "Нормаль до поверхні",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "ellipse",
          "title": "Еліпс",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "coordinate-system",
          "title": "Система координат",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "local-tangent-plane",
          "title": "Місцева дотична площина",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "great-circle-distance",
          "title": "Відстань великого кола (формула гаверсинусів)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "point-in-polygon",
          "title": "Належність точки багатокутнику (метод променя)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "shoelace-area",
          "title": "Орієнтована площа многокутника (формула шнурівки)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "hyperbola",
          "title": "Гіпербола",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "wgs84-datum",
          "title": "WGS-84: еліпсоїд і датум",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-figure-of-earth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-radii-of-curvature.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-datum-shift.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "geoid-and-amsl",
          "title": "Геоїд, AMSL і висота над еліпсоїдом",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-geoid.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-geoid-undulation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-geoid-lookup.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "ecef-ned-enu",
          "title": "ECEF, NED і ENU: земні й локальні системи координат",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-prime-meridian.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-ecef-to-geodetic.md",
              "status": "done"
            }
          ],
          "comp": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "map-projections",
          "title": "Картографічні проєкції та їхні спотворення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "math": [
            {
              "file": "math-tissot.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-impossible-map.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-distortion-map.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "web-mercator-tiles",
          "title": "Web Mercator і тайлова сітка",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-mercator-to-web.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-secant-integral.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-tile-coords.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "curvature-radius",
          "title": "Кривина й радіус кривини",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "vertical-datum",
          "title": "Вертикальний датум і національні системи висот",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "eci-frame",
          "title": "ECI: геоцентрична інерціальна система координат",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "rhumb-line",
          "title": "Локсодрома: лінія сталого курсу",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "triangulation-survey",
          "title": "Тріангуляція: як міряють великі відстані кутами",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "meusnier-theorem",
          "title": "Теорема Меньє: нормальний і косий перерізи",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "evolute",
          "title": "Еволюта плоскої кривої",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "minkowski-sum",
          "title": "Сума Мінковського: роздування однієї фігури іншою",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-minkowski-sum.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-support-function.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-convex-minkowski.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "gaussian-curvature",
          "title": "Гаусова кривина й чудова теорема",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-egregium.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-circle-defect.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-mesh-curvature.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "convex-set",
          "title": "Опукла множина",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "geodesic",
          "title": "Геодезична лінія: найкоротший шлях по поверхні",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gauss-bonnet",
          "title": "Теорема Гауса — Бонне",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "first-fundamental-form",
          "title": "Перша квадратична форма: метрика поверхні",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "mean-curvature",
          "title": "Середня кривина й мінімальні поверхні",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "developable-surface",
          "title": "Розгортні поверхні",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "supporting-hyperplane",
          "title": "Опорна гіперплощина й відокремлення: чому опукла множина є перетином півпросторів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "non-euclidean-geometry",
          "title": "Неевклідова геометрія й аксіома паралельних",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "second-fundamental-form",
          "title": "Друга квадратична форма й оператор форми",
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
      "slug": "trigonometry",
      "title": "Тригонометрія",
      "scope": "Тригонометричні функції, тотожності та обернені функції, кутові співвідношення в прямокутному трикутнику й на колі.",
      "topics": [
        {
          "slug": "atan2",
          "title": "atan2 — чотиричвертний арктангенс",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "hyperbolic-functions",
          "title": "Гіперболічні функції",
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
      "slug": "topology",
      "title": "Топологія",
      "scope": "Властивості просторів, інваріантні щодо неперервних деформацій, та їхні алгебраїчні інваріанти.",
      "topics": []
    },
    {
      "slug": "real-analysis",
      "title": "Аналіз",
      "scope": "Границі, диференціювання, інтегрування, теорія міри; включає гармонічний аналіз — ряди й перетворення Фур'є, вейвлети.",
      "topics": [
        {
          "slug": "time-and-frequency",
          "title": "Час і частота",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-fourier.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "fourier-idea",
          "title": "Ідея Фур'є",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "spectrum",
          "title": "Спектр",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "dft",
          "title": "ДПФ",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "windowing-leakage",
          "title": "Вікно й витік",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "derivative",
          "title": "Похідна",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "integral",
          "title": "Інтеграл",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "convolution",
          "title": "Згортка",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "extrema",
          "title": "Екстремуми",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "rms",
          "title": "RMS",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "sine-derivative",
          "title": "Похідна синуса",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "work-integral",
          "title": "Інтеграл роботи",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "half-power",
          "title": "Точка -3 дБ",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "logarithms",
          "title": "Логарифми",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "divergence",
          "title": "Дивергенція",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gauss-flux-theorem",
          "title": "Теорема Гаусса",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "z-transform",
          "title": "Z-перетворення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "time-frequency-tradeoff",
          "title": "Принцип невизначеності для сигналів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "fourier-series",
          "title": "Ряди Фур'є",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "taylor-series",
          "title": "Ряди Тейлора",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "numerical-differentiation",
          "title": "Чисельне диференціювання",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "numerical-integration",
          "title": "Чисельне інтегрування",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "impulse-response",
          "title": "Імпульсна характеристика",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "circular-convolution",
          "title": "Кільцева згортка",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "chain-rule",
          "title": "Ланцюгове правило",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "zero-padding",
          "title": "Zero-padding: інтерполяція спектра",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "hessian-matrix",
          "title": "Матриця Гессе й багатовимірні екстремуми",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "convex-functions",
          "title": "Опуклі функції й глобальний мінімум",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "improper-integral",
          "title": "Невласний інтеграл",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "lebesgue-integral",
          "title": "Інтеграл Лебега",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "line-integral",
          "title": "Криволінійний інтеграл",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "e-number",
          "title": "Число e",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "spectrogram",
          "title": "Спектрограма",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "psd",
          "title": "Спектральна щільність потужності (PSD)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "sampling-theorem",
          "title": "Теорема Найквіста — Шеннона про дискретизацію",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "dirichlet-kernel",
          "title": "Ядро Діріхле",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "parseval-theorem",
          "title": "Теорема Парсеваля і RMS гармонік",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "image-gradient",
          "title": "Градієнт зображення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gibbs-phenomenon",
          "title": "Явище Гіббса",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "universal-approximation",
          "title": "Теорема про універсальну апроксимацію",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "homogeneous-ode",
          "title": "Лінійні диференціальні рівняння: однорідне і частинний розв'язок",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "laplace-equation",
          "title": "Рівняння Лапласа і гармонічні функції",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "sequence-limit",
          "title": "Границя послідовності",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gradient",
          "title": "Градієнт",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "laplacian",
          "title": "Лапласіан: оператор ∇²",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "partial-derivative",
          "title": "Частинна похідна",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "implicit-function-theorem",
          "title": "Теорема про неявну функцію",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "elliptic-integral",
          "title": "Еліптичні інтеграли",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "geometric-series",
          "title": "Геометрична прогресія і сума ряду",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "lambert-w",
          "title": "W-функція Ламберта",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "rolle-theorem",
          "title": "Теорема Ролля і теорема про середнє значення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "spherical-harmonics",
          "title": "Сферичні гармоніки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gamma-function",
          "title": "Гамма-функція",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "stirling-approximation",
          "title": "Формула Стірлінга",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "differentiability",
          "title": "Диференційовність функції багатьох змінних",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "multiple-integral",
          "title": "Кратний інтеграл: інтегрування по площині й об'ємі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "inverse-function-theorem",
          "title": "Теорема про обернену функцію",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "supremum-infimum",
          "title": "Супремум та інфімум: точна верхня й нижня межа",
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
      "slug": "complex-analysis",
      "title": "Комплексний аналіз",
      "scope": "Голоморфні функції комплексної змінної, лишки та конформні відображення.",
      "topics": [
        {
          "slug": "phasors",
          "title": "Фазори",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "euler-formula",
          "title": "Формула Ейлера",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "impedance",
          "title": "Імпеданс",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "complex-numbers",
          "title": "Комплексні числа",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "roots-of-unity",
          "title": "Корені з одиниці",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "conformal-map",
          "title": "Конформне відображення",
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
      "slug": "functional-analysis",
      "title": "Функціональний аналіз",
      "scope": "Нескінченновимірні векторні простори, оператори та спектральна теорія на функціях.",
      "topics": [
        {
          "slug": "signal-orthogonality",
          "title": "Ортогональність сигналів",
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
      "slug": "differential-equations",
      "title": "Диференціальні рівняння",
      "scope": "Звичайні та частинні рівняння, що описують динаміку, і методи їх аналізу.",
      "topics": [
        {
          "slug": "capacitor-derivative",
          "title": "Похідна конденсатора",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "exponential-ode",
          "title": "Експоненційне ОДУ",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "rl-ode",
          "title": "ОДУ RL-кола",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "cascading",
          "title": "Каскадування фільтрів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "thomson-formula",
          "title": "Формула Томсона",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "damping",
          "title": "Загасання",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "laplace-transform",
          "title": "Перетворення Лапласа",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "bessel-functions",
          "title": "Функції Бесселя",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "legendre-polynomials",
          "title": "Многочлени та приєднані функції Лежандра",
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
      "slug": "probability",
      "title": "Імовірність",
      "scope": "Математична теорія випадковості — випадкові величини, процеси та граничні теореми.",
      "topics": [
        {
          "slug": "probability-basics",
          "title": "Імовірність як міра непевності",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "mean-variance",
          "title": "Середнє й дисперсія",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "central-limit",
          "title": "Центральна гранична теорема",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "thermal-fluctuations",
          "title": "Теплові флуктуації",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "bayesian-estimation",
          "title": "Байєсівське оцінювання",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "covariance-matrix-intuition",
          "title": "Матриця коваріації: інтуїція і геометрія",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gaussian-distribution",
          "title": "Нормальний розподіл",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "heavy-tail-distributions",
          "title": "Розподіли з важкими хвостами",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "characteristic-functions",
          "title": "Характеристичні функції",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "normal-distribution",
          "title": "Нормальний розподіл",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "covariance",
          "title": "Коваріація і кореляція",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "central-limit-theorem",
          "title": "Центральна гранична теорема",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "binomial-distribution",
          "title": "Біноміальний розподіл",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "poisson-process",
          "title": "Пуассонівський процес",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "order-statistics",
          "title": "Порядкові статистики",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "independent-trials",
          "title": "Незалежні спроби",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "littles-law",
          "title": "Закон Літтла",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "markov-chain",
          "title": "Ланцюги Маркова",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [
            {
              "file": "hist-markov.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-stationary.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-pagerank.md",
              "status": "done"
            }
          ],
          "comp": [],
          "api": []
        },
        {
          "slug": "random-walk",
          "title": "Випадкове блукання",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "birthday-paradox",
          "title": "Парадокс днів народжень",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "martingale",
          "title": "Мартингал",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "law-of-large-numbers",
          "title": "Закон великих чисел",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "value-of-information",
          "title": "Цінність інформації",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "system-reliability-math",
          "title": "Математика надійності систем",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "bayes-theorem",
          "title": "Теорема Баєса",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "hidden-markov-model",
          "title": "Прихована марковська модель",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "conditional-probability",
          "title": "Умовна ймовірність",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "coupon-collector",
          "title": "Задача про збирача купонів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "geometric-distribution",
          "title": "Геометричний розподіл",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "zipf-law",
          "title": "Закон Зіпфа: чому мала частка об'єктів забирає більшість звернень",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "exponential-distribution",
          "title": "Показниковий розподіл",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "branching-process",
          "title": "Процес розгалуження (Гальтона–Ватсона)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "circular-error-probable",
          "title": "Кругова ймовірна похибка: CEP, CE90 і перехід від еліпса до кола",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "chebyshev-inequality",
          "title": "Нерівність Чебишова",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "perron-frobenius-theorem",
          "title": "Теорема Перрона — Фробеніуса",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "update"
          },
          "hist": [
            {
              "file": "hist-perron-frobenius.md",
              "status": "done"
            }
          ],
          "comp": [],
          "math": [
            {
              "file": "math-dominant-eigenvector-proof.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-pagerank-power-iteration.md",
              "status": "done"
            }
          ],
          "api": []
        }
      ]
    },
    {
      "slug": "statistics",
      "title": "Статистика",
      "scope": "Висновки з даних — оцінювання, перевірка гіпотез, регресія та байєсів підхід.",
      "topics": [
        {
          "slug": "averaging",
          "title": "Усереднення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "noise-density",
          "title": "Густина шуму",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "accuracy",
          "title": "Точність і похибка",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "tolerance",
          "title": "Допуски",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "least-squares",
          "title": "Найменші квадрати",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "error-propagation",
          "title": "Додавання похибок",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "poisson-statistics",
          "title": "Статистика Пуассона",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "q-stability",
          "title": "Стабільність Q",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "averaging-gain",
          "title": "Виграш усереднення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "uncertainty-propagation",
          "title": "Поширення невизначеності",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "allan-variance",
          "title": "Дисперсія Аллана",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "sample-variance",
          "title": "Вибіркова дисперсія і поправка Бесселя",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "median-robust-stats",
          "title": "Медіана і робастна статистика",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "exponential-smoothing",
          "title": "Експоненційне згладжування (EMA)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "robust-averaging",
          "title": "Робасне усереднення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "weighted-average",
          "title": "Зважене середнє",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "correlation-coefficient",
          "title": "Коефіцієнт кореляції",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "goodness-of-fit",
          "title": "Якість підгонки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "weighted-least-squares",
          "title": "Зважений МНК",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "chi-squared-test",
          "title": "Критерій χ² Пірсона",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "percentiles-quantiles",
          "title": "Перцентилі й хвости",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "robust-estimators",
          "title": "Робастні оцінки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "hadamard-variance",
          "title": "Дисперсія Адамара",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "correlation-causation",
          "title": "Кореляція і причинність",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "confidence-interval",
          "title": "Довірчий інтервал",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "multiple-comparisons",
          "title": "Множинні порівняння та поправки на них",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        }
      ]
    },
    {
      "slug": "optimization",
      "title": "Оптимізація",
      "scope": "Пошук екстремумів за обмежень — лінійне, опукле й дискретне програмування; включає теорію керування: системи зі зворотним зв'язком.",
      "topics": [
        {
          "slug": "step-response",
          "title": "Крокова відповідь",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "feedforward",
          "title": "Феєдфорвард",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "pid-calculus",
          "title": "ПІД-регулятор",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "derivative-filter",
          "title": "Фільтрація D-члена: смугообмежений диференціатор",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "phase-lead-lag",
          "title": "Фазо-випереджаючі та фазо-відстаючі ланки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "integrator-windup",
          "title": "Накопичувальне насичення (windup)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "nyquist-criterion",
          "title": "Критерій Найквіста",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "conditional-stability",
          "title": "Умовна стійкість",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "positive-feedback",
          "title": "Додатний зворотний зв'язок",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "block-diagram-algebra",
          "title": "Алгебра блок-схем",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "anti-windup",
          "title": "Анти-windup",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gain-scheduling",
          "title": "Gain scheduling",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "relay-autotuning",
          "title": "Relay-автоналаштування",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "bang-bang-control",
          "title": "Дворежимний регулятор",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "lyapunov-stability",
          "title": "Стійкість за Ляпуновим",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gauss-newton",
          "title": "Метод Ґаусса–Ньютона",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "levenberg-marquardt",
          "title": "Метод Левенберґа–Марквардта",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "linear-complementarity",
          "title": "Задача лінійної доповняльності",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        }
      ]
    },
    {
      "slug": "game-theory",
      "title": "Теорія ігор",
      "scope": "Математика стратегічної взаємодії, рівноваг і прийняття рішень за конфлікту.",
      "topics": []
    },
    {
      "slug": "information-theory",
      "title": "Теорія інформації",
      "scope": "Кількісна міра інформації, ентропія, кодування та межі передавання й стиснення.",
      "topics": [
        {
          "slug": "hamming-distance",
          "title": "Відстань Гемінга",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "proj": [
            {
              "file": "proj-popcount-distance.md",
              "status": "done"
            }
          ],
          "hist": [],
          "comp": [],
          "math": [],
          "api": []
        },
        {
          "slug": "kraft-inequality",
          "title": "Нерівність Крафта",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "source-coding-theorem",
          "title": "Теорема Шеннона про кодування джерела",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "kl-divergence",
          "title": "Розбіжність Кульбака–Лейблера",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "weight-distribution",
          "title": "Ваговий розподіл коду",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "coding-bounds",
          "title": "Межі на коди: Сінглтон, Плоткін, Гілберт–Варшамов",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "singleton-bound",
          "title": "Межа Сінглтона",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "complete-codes",
          "title": "Повні коди та рівність Крафта",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "rary-codes",
          "title": "Коди над r-арним алфавітом",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gibbs-inequality",
          "title": "Нерівність Гіббса",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "uniquely-decodable-codes",
          "title": "Однозначно декодовні коди",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "information-entropy",
          "title": "Інформаційна ентропія Шеннона",
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
      "slug": "numerical-analysis",
      "title": "Числові методи",
      "scope": "Алгоритми наближеного розв'язання математичних задач і аналіз їхньої похибки та збіжності.",
      "topics": [
        {
          "slug": "ieee754",
          "title": "IEEE 754",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "si-prefixes",
          "title": "Префікси СІ",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "dimensional-analysis",
          "title": "Розмірний аналіз",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "e-series",
          "title": "Ряди E",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "energy-units",
          "title": "Одиниці енергії",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "ppm",
          "title": "PPM",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "error-budget",
          "title": "Бюджет похибок",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "inverse-problem",
          "title": "Обернена задача вимірювання",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "buckingham-pi-theorem",
          "title": "Теорема Бекінгема (Π-теорема)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "preferred-numbers",
          "title": "Переважні числа (ряди Ренара)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "tolerance-stack",
          "title": "Накопичення допусків у ланцюжку",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "monte-carlo-propagation",
          "title": "Метод Монте-Карло для поширення похибок",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "tolerance-stackup",
          "title": "Складання допусків",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "float-arithmetic-error",
          "title": "Модель похибки операцій з плаваючою комою",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "scientific-notation",
          "title": "Наукова та інженерна нотація",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "unit-conversion",
          "title": "Переведення одиниць",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "numeric-stability",
          "title": "Чисельна стійкість алгоритмів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "dct",
          "title": "Дискретне косинусне перетворення (DCT)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "dft-spectrum",
          "title": "Дискретне перетворення Фур'є",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "window-functions",
          "title": "Віконні функції у спектральному аналізі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "polynomial-fit",
          "title": "Підгонка полінома",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "aliasing",
          "title": "Аліасинг (теорема Найквіста)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "fixed-point-iteration",
          "title": "Ітерація нерухомої точки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "newton-raphson",
          "title": "Метод Ньютона — Рафсона",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "order-of-magnitude-estimation",
          "title": "Оцінка порядку величини",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "done"
          },
          "hist": [],
          "comp": [],
          "math": [],
          "proj": [],
          "api": []
        },
        {
          "slug": "karhunen-loeve-transform",
          "title": "Перетворення Карунена–Лоева (KLT)",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "shadowing-lemma",
          "title": "Лема про тінь: чи справжня порахована траєкторія",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gauss-seidel",
          "title": "Метод Гаусса–Зейделя",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "bisection",
          "title": "Метод ділення відрізка навпіл",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "finite-difference-method",
          "title": "Метод скінченних різниць",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "von-neumann-stability",
          "title": "Аналіз стійкості за фон Нейманом",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "bilinear-interpolation",
          "title": "Білінійна інтерполяція",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "sparse-jacobian-coloring",
          "title": "Оцінювання розрідженого якобіана: розфарбування графа",
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
