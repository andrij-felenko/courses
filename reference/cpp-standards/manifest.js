window.__BOOKS__ = window.__BOOKS__ || [];
window.__BOOKS__.push(
{
  "type": "reference",
  "slug": "cpp-standards",
  "title": "Стандарти C++",
  "sections": [
    {
      "slug": "language",
      "title": "Механіка мови",
      "scope": "Правила, за якими компілятор розуміє код: категорії значень, посилання, винятки, зв'язування.",
      "topics": [
        {
          "slug": "value-categories",
          "title": "Категорії значень: lvalue, prvalue, xvalue",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-value-categories.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-category-probe.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "move-semantics",
          "title": "Семантика переміщення і rvalue-посилання",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-move-proposal.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-buffer-move.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "rule-of-five-zero",
          "title": "Правило п'яти й правило нуля",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-three-five-zero.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-special-members.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-copy-and-swap.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "copy-elision",
          "title": "Усунення копій і гарантований RVO",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-guaranteed-elision.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-copy-probe.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "references-binding",
          "title": "Посилання і правила зв'язування",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-references-birth.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-binding-lab.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "perfect-forwarding",
          "title": "Ідеальне передавання й універсальні посилання",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-forwarding-problem.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-forwarding-factory.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "const-correctness",
          "title": "Коректність за const",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-const-origin.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-logical-const-cache.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-const-toolbox.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "auto-type-deduction",
          "title": "auto й виведення типу",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-auto-decltype.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-deduction-lab.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "initialization-forms",
          "title": "Форми ініціалізації та найприкріший розбір",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-uniform-init.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-which-ctor.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "lambdas-and-captures",
          "title": "Лямбди й захоплення: що живе скільки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-lambda-birth.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-callback-registry.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-capture-forms.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "exceptions-mechanism",
          "title": "Винятки: кидання, розкрутка стека, перехоплення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-exceptions-birth.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-exception-boundary.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-unwind-abi.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "exception-safety-guarantees",
          "title": "Гарантії безпеки винятків: базова, сильна, nothrow",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-cargill-abrahams.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-throwing-test.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-stdlib-guarantees.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "noexcept",
          "title": "noexcept: обіцянка й наслідки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-exception-specifications.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-noexcept-vector-growth.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "odr-and-linkage",
          "title": "Правило одного визначення й зв'язування імен",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-linkage-table.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-odr-break.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "namespaces-and-adl",
          "title": "Простори імен і пошук, залежний від аргументів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-koenig-lookup.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-adl-lab.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "decltype",
          "title": "decltype: тип виразу разом із його категорією",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-expression-detection.md",
              "status": "done"
            },
            {
              "file": "proj-transparent-wrapper.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "overload-resolution",
          "title": "Розв'язання перевантажень: як обирається функція",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-ranking-rules.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-overloading-birth.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-overload-lab.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "deducing-this",
          "title": "Явний параметр об'єкта (deducing this)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-deducing-this.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-self-deduced-mixin.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "structured-bindings",
          "title": "Структуровані зв'язування: auto [a, b]",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-structured-bindings.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-tuple-like.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "range-based-for",
          "title": "Цикл for за діапазоном і в що він розгортається",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-range-for-papers.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-sentinel-range.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "coroutines",
          "title": "Корутини: призупинення функції й час життя кадру",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-promise-and-awaiter.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-coroutines-in-cpp.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-generator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "rtti-and-dynamic-cast",
          "title": "RTTI: typeid і dynamic_cast",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-rtti-proposal.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-llvm-style-rtti.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-typeid-dynamic-cast.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "swap-operation",
          "title": "Обмін значеннями: swap, ADL-пошук і зобов'язання не кидати",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-swap-idiom.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-swap-facilities.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "constexpr-and-consteval",
          "title": "constexpr і consteval: обчислення під час компіляції",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-constexpr-birth.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-constexpr-by-version.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-compile-time-table.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "name-mangling",
          "title": "Спотворення імен: як символ несе сигнатуру",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "cpp-modules",
          "title": "Модулі C++20: інтерфейс замість заголовка",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "using-and-name-hiding",
          "title": "Затуляння імен і using-оголошення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "cast-operators",
          "title": "Оператори приведення: static_cast, reinterpret_cast, const_cast",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "multiple-and-virtual-inheritance",
          "title": "Множинне й віртуальне спадкування: розкладка підобʼєктів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "constinit",
          "title": "constinit: ініціалізація до запуску без обіцянки незмінності",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "empty-base-optimization",
          "title": "Оптимізація порожньої бази й [[no_unique_address]]",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "three-way-comparison",
          "title": "Тричленне порівняння (operator<=>) і переписані кандидати",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "static-reflection",
          "title": "Статична рефлексія C++26: оператор ^^, splice і consteval-метафункції",
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
      "slug": "lifetime",
      "title": "Об'єкти, володіння, пам'ять",
      "scope": "Хто чим володіє, коли об'єкт живий і звідки береться пам'ять.",
      "topics": [
        {
          "slug": "object-lifetime",
          "title": "Час життя об'єкта",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-manual-lifetime.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-temporary-extension.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "unique-ptr",
          "title": "unique_ptr: одноосібне володіння",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-auto-ptr.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-c-handle-owner.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "shared-weak-ptr",
          "title": "shared_ptr і weak_ptr: спільне володіння й розрив циклів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-shared-ptr-birth.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-shared-weak.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-weak-cache.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "ownership-semantics",
          "title": "Володіння в сигнатурі: що означає тип параметра",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-ownership-conventions.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-parameter-passing.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-ownership-refactor.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "dangling-references",
          "title": "Висячі посилання й звернення після звільнення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "new-delete-allocation",
          "title": "new, delete й шляхи виділення пам'яті",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "custom-allocators",
          "title": "Власні алокатори й пам'ять під контролем",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "pimpl",
          "title": "PIMPL: сховати реалізацію за вказівником",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "alignment-placement-new",
          "title": "Вирівнювання й розміщувальний new",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "virtual-destructor",
          "title": "Віртуальний деструктор і поліморфне видалення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "scope-guard",
          "title": "Охоронець області: відкат через деструктор",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "std-launder",
          "title": "std::launder і повторне використання сховища",
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
      "slug": "templates",
      "title": "Шаблони й узагальнений код",
      "scope": "Як з одного тексту постає багато типів — і скільки це коштує.",
      "topics": [
        {
          "slug": "templates-basics",
          "title": "Шаблони: параметризація типом",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "template-argument-deduction",
          "title": "Виведення аргументів шаблону",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "specialization-overload",
          "title": "Спеціалізація й перевантаження шаблонів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "variadic-and-folds",
          "title": "Шаблони змінної арності й вирази згортки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "sfinae-and-enable-if",
          "title": "SFINAE й enable_if: відбір перевантажень",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "concepts-constraints",
          "title": "Концепти й обмеження шаблонів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "constexpr-if",
          "title": "if constexpr: гілка, якої не існує",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "type-traits",
          "title": "Риси типів (type traits)",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-type-traits-ref.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-type-traits-evolution.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-custom-trait-impl.md",
              "status": "done"
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
          "slug": "crtp",
          "title": "CRTP: статичний поліморфізм",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-crtp-patterns.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-crtp-origin.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-crtp-mixin.md",
              "status": "done"
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
          "slug": "instantiation-cost",
          "title": "Ціна інстанціювання: час компіляції й розмір бінарника",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-compiler-diagnostics.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-template-bloat.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-instantiation-profiling.md",
              "status": "done"
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
          "slug": "expression-templates",
          "title": "Шаблони виразів: коли вираз стає деревом типів",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-expression-interface.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-expression-templates.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-expression-vector.md",
              "status": "done"
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
          "slug": "two-phase-name-lookup",
          "title": "Двофазний пошук імен у шаблонах",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-two-phase-rules.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-two-phase-lookup.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-lookup-diagnostics.md",
              "status": "done"
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
          "slug": "customization-points",
          "title": "Точки налаштування й об'єкти-CPO",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-cpo-implementations.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-customization-evolution.md",
              "status": "done"
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
      "slug": "library",
      "title": "Стандартна бібліотека",
      "scope": "Що дає стандартна бібліотека і як вибір її засобу впливає на швидкодію.",
      "topics": [
        {
          "slug": "stl-containers-choice",
          "title": "Контейнери STL: вибір під задачу і ціна операцій",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-invalidation-rules.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-stl-design.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-container-benchmarks.md",
              "status": "done"
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
          "slug": "iterators-model",
          "title": "Ітератори: категорії й модель обходу",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-iterator-traits.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-iterator-evolution.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-custom-range-iterator.md",
              "status": "done"
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
          "slug": "stl-algorithms",
          "title": "Алгоритми STL замість ручних циклів",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-algorithms-toolbox.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-stl-birth.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-custom-iterator-algo.md",
              "status": "done"
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
          "slug": "string-and-string-view",
          "title": "string і string_view: володіти чи дивитися",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-string-view-ops.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-string-view.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-custom-parser.md",
              "status": "done"
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
          "slug": "span-contiguous",
          "title": "span: невласницький вид на суцільні дані",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-span-interface.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-span-evolution.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-zero-copy-buffer.md",
              "status": "done"
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
          "slug": "optional",
          "title": "optional: значення, якого може не бути",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-optional-ops.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-optional-origin.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-optional-pipeline.md",
              "status": "done"
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
          "slug": "variant-and-visit",
          "title": "variant і visit: одне з кількох",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-variant-interface.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-variant-evolution.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-ast-visitor.md",
              "status": "done"
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
          "slug": "expected-error-handling",
          "title": "expected: помилка як значення",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-expected-monadic-ops.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-error-handling-evolution.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-expected-pipeline.md",
              "status": "done"
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
          "slug": "std-function-type-erasure",
          "title": "std::function і стирання типу: ціна колбека",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-std-function-toolbox.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-type-erasure-evolution.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-custom-type-erasure.md",
              "status": "done"
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
          "slug": "chrono",
          "title": "chrono: годинники, точки часу й тривалості",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-chrono-type-system.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-chrono-evolution.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-high-res-timer.md",
              "status": "done"
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
          "slug": "std-filesystem",
          "title": "filesystem: шляхи й дії з файлами переносно",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-path-and-ops.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-boost-filesystem.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-file-analyzer.md",
              "status": "done"
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
          "slug": "ranges-pipelines",
          "title": "Ranges: конвеєри перетворень і ліниві види",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-range-adaptors.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-ranges-birth.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-custom-range-adaptor.md",
              "status": "done"
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
          "slug": "format-and-print",
          "title": "format і print: типобезпечне форматування",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-format-specifiers.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-format-evolution.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-custom-formatter.md",
              "status": "done"
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
          "slug": "std-random",
          "title": "random: рушії, розподіли й відтворюваність",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-random-toolbox.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-pcg-mersenne.md",
              "status": "done",
          "math": [
            {
              "file": "math-distributions.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-random-benchmarks.md",
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
          "slug": "std-exception-hierarchy",
          "title": "Ієрархія std::exception і власні типи винятків",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-exception-classes.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-exception-hierarchy.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-custom-exception-tree.md",
              "status": "done"
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
          "slug": "tuple-and-pair",
          "title": "tuple і pair: кортеж значень різних типів",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-tuple-and-pair.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-tuple-evolution.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-tuple-utilities.md",
              "status": "done"
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
          "slug": "std-generator",
          "title": "std::generator: лінива послідовність на корутині",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-generator-ref.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-coroutines-evolution.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-lazy-pipeline.md",
              "status": "done"
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
          "slug": "iterator-invalidation",
          "title": "Інвалідація ітераторів: коли посилання на елемент стає недійсним",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-invalidation-matrix.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-iterator-invalidation.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-invalidation-detector.md",
              "status": "done"
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
      "slug": "concurrency",
      "title": "Багатопотоковість у C++",
      "scope": "Стандартні засоби паралельності: потоки, синхронізація, асинхронний результат.",
      "topics": [
        {
          "slug": "std-thread-jthread",
          "title": "thread і jthread: запуск, приєднання, скасування",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-thread-jthread.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-thread-evolution.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-jthread-pipeline.md",
              "status": "done"
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
          "slug": "mutex-and-raii-locks",
          "title": "М'ютекс і RAII-замки: lock_guard, unique_lock, scoped_lock",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-locks-reference.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-mutex-origins.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-bank-transfer.md",
              "status": "done"
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
          "slug": "condition-variable",
          "title": "Умовна змінна: чекати подію, а не крутитися",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-cv-reference.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-cv-origin.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-bounded-queue.md",
              "status": "done"
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
          "slug": "shared-mutex",
          "title": "shared_mutex: багато читачів, один письменник",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-shared-mutex.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-shared-mutex.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-shared-cache.md",
              "status": "done"
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
          "slug": "future-promise",
          "title": "future й promise: результат з іншого потоку",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-future-promise.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-future-promise.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-custom-future.md",
              "status": "done"
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
          "slug": "async-and-packaged-task",
          "title": "async і packaged_task: запуск із результатом",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-async-packaged-task.md",
              "status": "done",
          "hist": [
            {
              "file": "hist-async-task-evolution.md",
              "status": "done",
          "proj": [
            {
              "file": "proj-task-executor.md",
              "status": "done"
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
          "slug": "thread-local",
          "title": "thread_local: стан, приватний для потоку",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "latch-barrier-semaphore",
          "title": "latch, barrier і counting_semaphore",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "stop-token",
          "title": "stop_token: кооперативне скасування",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "parallel-algorithms",
          "title": "Політики виконання й паралельні алгоритми",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "call-once-lazy-init",
          "title": "call_once і once_flag: одноразова ініціалізація",
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
      "slug": "releases",
      "title": "Випуски стандарту",
      "scope": "Що приніс кожен реліз мови й на що можна спиратися в конкретному проєкті.",
      "topics": [
        {
          "slug": "standardization-process",
          "title": "Як робиться стандарт C++: комітет, папери, цикл",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "cpp11-cpp14",
          "title": "C++11 і C++14: перелом",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "cpp17-features",
          "title": "Що приніс C++17",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "cpp20-features",
          "title": "Що приніс C++20",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "cpp23-features",
          "title": "Що приніс C++23",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "compiler-support",
          "title": "Підтримка стандартів компіляторами й прапорці",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "migrating-standards",
          "title": "Перехід проєкту на новіший стандарт",
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
      "slug": "practice",
      "title": "Ремесло великого проєкту",
      "scope": "Те, що болить саме у великій C++-базі: межі бінарників, заголовки, час збірки.",
      "topics": [
        {
          "slug": "abi-stability-cpp",
          "title": "Стабільність ABI у C++ і що її ламає",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "header-hygiene",
          "title": "Гігієна заголовків і час перезбірки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "extern-c-interop",
          "title": "extern \"C\" і сумісність із C-інтерфейсами",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "core-guidelines",
          "title": "Core Guidelines: узгоджені правила стилю й безпеки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "pending"
          }
        },
        {
          "slug": "gsl-support-library",
          "title": "GSL: not_null, owner і решта підпірок Core Guidelines",
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
