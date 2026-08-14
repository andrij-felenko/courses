window.__BOOKS__ = [
  {
    "type": "reference",
    "slug": "unix-linux",
    "title": "Unix і Linux",
    "sections": [
      {
        "slug": "virtualization-and-containers",
        "title": "Віртуалізація й контейнери",
        "scope": "KVM, namespaces, cgroups як основа ізоляції",
        "topics": [
          { slug: "kvm-and-qemu-architecture", title: "Архітектура KVM і QEMU: як ядро віддає процесор гостю", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-kvm-ioctl.md", status: "done" }] , "hist": [{ file: "hist-kvm-creation.md", status: "done" }] , "proj": [{ file: "proj-kvm-mini-hypervisor.md", status: "done" }] },
        ]
      },
      {
        "slug": "storage",
        "title": "Сховище",
        "scope": "блокові пристрої, розділи, RAID, файлові системи на диску",
        "topics": [
        ]
      },
      {
        "slug": "proc",
        "title": "Псевдофайлові системи",
        "scope": "procfs, sysfs, debugfs та інші вікна ядра у простір користувача",
        "topics": [
          { slug: "tmpfs-shmem-ram-filesystem", title: "Тимчасова ВФС tmpfs та підсистема shmem: дисковий кеш у RAM", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-tmpfs-mount-and-shmem-sysctl.md", status: "done" }] , "hist": [{ file: "hist-ramdisk-to-tmpfs.md", status: "done" }] , "proj": [{ file: "proj-posix-shm-and-memfd.md", status: "done" }] },
          { slug: "sysfs-kobject-sysfs-dirent", title: "Файлова система sysfs, kobject та sysfs_dirent", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-sysfs-kobject.md", status: "done" }] , "hist": [{ file: "hist-sysfs-birth.md", status: "done" }] , "proj": [{ file: "proj-kobject-custom.md", status: "done" }] },
          { slug: "sysctl-kernel-tuning-interface", title: "Інтерфейс тюнінгу ядра sysctl та /proc/sys", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-sysctl-handlers.md", status: "done" }] , "hist": [{ file: "hist-sysctl-evolution.md", status: "done" }] , "proj": [{ file: "proj-sysctl-tool.md", status: "done" }] },
          {
            "slug": "psi-pressure-stall-information",
            "title": "Підсистема оцінки голодування ресурсів PSI (Pressure Stall Info)",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-proc-pressure-interface.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-loadavg-to-psi.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-psi-daemon.md",
                "status": "done",
            "api": [
              {
                "file": "api-proc-pressure-interface.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-loadavg-to-psi.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-psi-daemon.md",
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
              "status": "done"
            }
          },
          { slug: "procfs-architecture-and-proc-pid", title: "Архітектура procfs та структура /proc/[pid]", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-proc-pid-nodes.md", status: "done" }] , "hist": [{ file: "hist-procfs-evolution.md", status: "done" }] , "proj": [{ file: "proj-procfs-pid-inspector.md", status: "done" }] },
          { slug: "kernfs-vfs-abstraction-layer", title: "Шар абстракції kernfs та його роль у розвантаженні VFS", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-kernfs-ops.md", status: "done" }] , "hist": [{ file: "hist-kernfs-evolution.md", status: "done" }] , "proj": [{ file: "proj-kernfs-custom-fs.md", status: "done" }] },
          { slug: "hugetlbfs-and-transparent-hugepages", title: "Файлова система hugetlbfs та прозорі великі сторінки THP", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-hugetlb-thp-sysfs.md", status: "done" }] , "hist": [{ file: "hist-hugepages-evolution.md", status: "done" }] , "proj": [{ file: "proj-hugepages-allocator.md", status: "done" }] },
          { slug: "devtmpfs-kernel-device-node-management", title: "Автоматичне монтування вузлів пристроїв у devtmpfs", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-devtmpfs-kernel-surface.md", status: "done" }] , "hist": [{ file: "hist-dev-nodes-evolution.md", status: "done" }] , "proj": [{ file: "proj-devtmpfs-node-inspector.md", status: "done" }] },
          { slug: "debugfs-tracefs-kernel-debugging-interfaces", title: "Налагодові ВФС: debugfs та tracefs", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-debugfs-tracefs-control.md", status: "done" }] , "hist": [{ file: "hist-debugfs-tracefs-evolution.md", status: "done" }] , "proj": [{ file: "proj-kernel-debugfs-module.md", status: "done" }] },
          { slug: "configfs-user-space-kernel-object-creation", title: "Файлова система configfs: створення ядерних об'єктів із юзерспейсу", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-configfs-structures.md", status: "done" }] , "hist": [{ file: "hist-configfs-evolution.md", status: "done" }] , "proj": [{ file: "proj-configfs-kernel-module.md", status: "done" }] },
          { slug: "cgroupfs-v1-v2-resource-management-tree", title: "cgroupfs v1 та v2: ієрархічне дерево керування ресурсами", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-cgroupv2-control-files.md", status: "done" }] , "hist": [{ file: "hist-cgroups-evolution.md", status: "done" }] , "proj": [{ file: "proj-cgroupv2-manager.md", status: "done" }] },
          { slug: "bpffs-bpf-filesystem-and-map-pinning", title: "Файлова система bpffs та пінінг об'єктів BPF (maps, programs)", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-bpffs-syscall-and-ops.md", status: "done" }] , "hist": [{ file: "hist-bpffs-evolution.md", status: "done" }] , "proj": [{ file: "proj-pinned-map-sharing.md", status: "done" }] },
        ]
      },
      {
        "slug": "foundations",
        "title": "Ідея та родовід",
        "scope": "Звідки Unix узявся, які рішення в ньому засадничі й що з них випливає для всього іншого.",
        "topics": [
          {
            "slug": "unix-philosophy",
            "title": "Філософія Unix: малі програми, що складаються",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-filter-contract.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-pipeline-by-hand.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "everything-is-a-file",
            "title": "«Усе є файлом»: один інтерфейс на все",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-one-namespace.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-uniform-copy.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-and-userspace",
            "title": "Ядро й простір користувача",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-border-origin.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-border-probe.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "syscall-mechanics",
            "title": "Системний виклик: як програма просить ядро",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "proj": [
                {
                  "file": "proj-entry-path-walk.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "unix-lineage",
            "title": "Родовід Unix: AT&T, BSD і поява Linux",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-multics.md",
                  "status": "done"
                },
                {
                  "file": "hist-usl-bsdi.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-portable-c.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "posix-standard",
            "title": "POSIX: що саме стандартизовано",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-conformance-query.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-standard-wars.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-portable-shell.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-vs-distribution",
            "title": "Ядро, дистрибутив і що між ними",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-first-distributions.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-min-userland.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "gnu-userland",
            "title": "Інструментарій GNU і чому «GNU/Linux»",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-gnu-vs-posix.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-two-halves.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-minimal-userland.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "libc-as-gateway",
            "title": "libc як шлюз до ядра",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-libc-boundary.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-libc-story.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-syscall-without-libc.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "monolithic-with-modules",
            "title": "Монолітне ядро з модулями: вибір Linux",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-tanenbaum-torvalds.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-hello-module.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "userspace-abi-stability",
            "title": "Що саме заморожено: ABI до простору користувача",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-abi-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-vsyscall-trap.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-abi-extensible-syscall.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-abi-stability",
            "title": "«Не ламати простір користувача»: сталість ABI ядра",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-do-not-break.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-feature-probe.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-release-model",
            "title": "Модель випусків ядра: вікно злиття, -rc і стабільні гілки",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-release-metadata.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-two-branches.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-where-is-my-fix.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-timekeeping",
            "title": "Час у ядрі: тики, монотонний годинник і джерела часу",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-tick-to-tickless.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-clock-lab.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-cycles-to-nanoseconds.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "compat-32-on-64",
            "title": "32-бітні програми на 64-бітному ядрі: шар сумісности",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-compat-contract.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-64bit-transition.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-see-the-seam.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-cve-and-security-fixes",
            "title": "CVE в ядрі: потік номерів і що з ним робити",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-cve-record.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-kernel-becomes-cna.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-cve-triage.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "time-representation-y2038",
            "title": "Час як число: time_t, епоха і межа 2038 року",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-time64-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-epoch-choice.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-y2038-audit.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-config-and-build",
            "title": "Конфігурація й збірка ядра: Kconfig, .config і що потрапляє в образ",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-kconfig-language.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-config-wars.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-trace-one-option.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "sysctl-tunables",
            "title": "sysctl: параметри ядра, які крутять на ходу",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sysctl-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-mib-to-files.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-own-sysctl.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-text-patching",
            "title": "Правка коду ядра на ходу: alternatives, static keys й text_poke",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-kernel-self-editing.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-static-key-module.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "livepatch",
            "title": "Живе латання ядра: livepatch і модель узгодженості",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-livepatch-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-ksplice-to-livepatch.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-livepatch-module.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-taint",
            "title": "Заплямоване ядро: прапорці taint і що вони означають при розборі аварій",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-taint-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-taint-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-taint-lab.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "sparse-checker",
            "title": "sparse: статичний перевіряч ядра й анотації на кшталт __iomem",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-annotations.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-check-driver.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "plan-9-and-9p",
            "title": "Plan 9 і протокол 9P: «усе є файлом», доведене до мережі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-9p-protocol.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-bell-labs-plan9.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-v9fs-wsl2.md",
                  "status": "done"
                }
              ]
            }
          }
        ]
      },
      {
        "slug": "processes",
        "title": "Процес",
        "scope": "Процес як головна одиниця системи: як народжується, як планується, як ізолюється.",
        "topics": [
          { slug: "rcu-read-copy-update", title: "RCU: читання без замків і відкладене звільнення", basic: { status: "done" }, detailed: { status: "done" } },
          { slug: "namespace-deep-dive", title: "Простори імен: глибокий семантичний розбір (Namespace Deep Dive)", basic: { status: "done" }, detailed: { status: "done" } },
          { slug: "futex-fast-userspace-mutex", title: "Futex (Fast Userspace Mutex)", basic: { status: "done" }, detailed: { status: "done" } , "api": [{ file: "api-futex-syscall.md", status: "done" }] , "hist": [{ file: "hist-futex-evolution.md", status: "done" }] , "proj": [{ file: "proj-futex-mutex.md", status: "done" }] },
          { slug: "cgroup-v2-controllers", title: "Контролери Cgroups v2: механізми розподілу та лімітування ресурсів", basic: { status: "done" }, detailed: { status: "done" } },
          { slug: "atomics-and-memory-barriers", title: "Атомарні операції та бар'єри пам'яті в Linux", basic: { status: "done" }, detailed: { status: "done" } },
          {
            "slug": "systemd-architecture-and-cgroups",
            "title": "Архітектура systemd та cgroups",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "seqlocks",
            "title": "Послідовні замки: як читати без блокування письменників",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "process-model",
            "title": "Процес: що це насправді",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-process-and-fork.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-clone-flags.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "pid-and-hierarchy",
            "title": "PID і дерево процесів",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-pid-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-pid-and-init.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-pidfd-supervisor.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "fork-semantics",
            "title": "fork: розмноження процесу",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-fork-origin.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-cow-observed.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "exec-semantics",
            "title": "exec: заміна образу",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-exec-family.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-shebang.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-exec-survivors.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "exit-wait-zombies",
            "title": "Завершення, wait і зомбі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-wait-family.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-wait-and-zombie.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-zombie-lab.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "orphan-reparenting",
            "title": "Сироти й перепідпорядкування",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-orphan-and-subreaper.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-reparenting-lab.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "process-states",
            "title": "Стани процесу і що означає стан D",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-state-reporting.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-killable-sleep.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-catch-d-state.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "ptrace-and-debugging",
            "title": "ptrace: повний контроль над чужим процесом",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "scheduler-model",
            "title": "Планувальник: як ядро ділить час",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-scheduler-evolution.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-share-experiment.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-virtual-time.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "priority-nice-realtime",
            "title": "Пріоритети, nice і реальночасові класи",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sched-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-nice-to-deadline.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-realtime-thread.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-shares-and-bandwidth.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "threads-as-tasks",
            "title": "Потоки в Linux: задача як одиниця планування",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-per-thread-scope.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-linuxthreads-to-nptl.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-thread-anatomy.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "cgroups",
            "title": "cgroups: облік і обмеження ресурсів",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-cgroup2-interface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-two-hierarchies.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-cgroup-by-hand.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "namespaces",
            "title": "Простори імен: ізоляція погляду на систему",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-namespace-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-namespaces-origin.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-mini-container.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "spawn-alternatives",
            "title": "vfork, posix_spawn і clone: чим ще народжують процес",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-clone-flags.md",
                  "status": "done"
                },
                {
                  "file": "api-posix-spawn.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-spawn-cost.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "resource-limits",
            "title": "Ліміти ресурсів: rlimit і ulimit",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-rlimit.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-limits-lineage.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-fd-limit.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "cpu-time-accounting",
            "title": "Облік процесорного часу: як ядро набирає user і sys",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-cputime-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-tick-accounting.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-utime-vs-runtime.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-sampling-error.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "daemonize",
            "title": "Демонізація: відхід у фон",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-daemon-word.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-daemonize.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "cpu-affinity",
            "title": "Прив'язка задач до ядер: affinity, taskset і cpuset",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-affinity-interfaces.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-isolated-core.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-preemption",
            "title": "Витісненість ядра: від PREEMPT_NONE до PREEMPT_RT",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-preempt-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-preemptible-kernel.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-measure-latency.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-threads",
            "title": "Потоки ядра: задачі без простору користувача",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-kthread-names.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-daemonize-to-kworkers.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-kthread-module.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "binfmt-misc",
            "title": "binfmt_misc: як ядро вчиться запускати чужі формати",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-register-format.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-binfmt-misc.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-register-own-format.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-wait-queues",
            "title": "Черги очікування в ядрі: як задача засинає й прокидається",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-wait-queue-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-sleep-and-wakeup.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-waitqueue-driver.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "atomic-ops",
            "title": "Атомарні операції",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-kernel-atomic-ops.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-atomic-instructions.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-lockfree-ringbuffer.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "memory-barriers",
            "title": "Бар'єри пам'яті: впорядкування операцій",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-kernel-memory-barriers.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-out-of-order-cpu.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-lockfree-stack.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-locking",
            "title": "Замки в ядрі й атомарний контекст: де спати не можна",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-locking-primitives.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-lockdep-lab.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-lock-scaling.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "per-cpu-data",
            "title": "Дані свого ядра процесора: змінні per-CPU і local_lock",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-percpu.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-percpu-and-local-lock.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-percpu-stats.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "checkpoint-restore",
            "title": "Контрольна точка й відновлення процесу (CRIU)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-kernel-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-two-schools.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-inject-parasite.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-precopy-convergence.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "cpu-hotplug",
            "title": "Вимикання ядер процесора на ходу: online, offline і хто про це має знати",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-hotplug-sysfs.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-notifier-to-state-machine.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-cpuhp-module.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "rseq",
            "title": "Перезапускні послідовності (rseq): ділянки без замків, які починаються заново",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-rseq.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-rseq-journey.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-percpu-counter.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "stop-machine",
            "title": "stop_machine: зупинити всю машину, щоб змінити недоторканне",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-birth-and-retreat.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-freeze-cost.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "membarrier",
            "title": "membarrier: примусовий бар'єр пам'яті на всіх ядрах процесу",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-membarrier.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-urcu-and-membarrier.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-asymmetric-rcu.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "pidfd",
            "title": "Дескриптор процесу (pidfd)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-pidfd-info.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-pdfork-to-pidfd.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-peer-identity.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "cpu-isolation",
            "title": "Ізоляція ядер процесора: isolcpus, nohz_full і боротьба за тишу на гарячому ядрі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-isolation-knobs.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-tickless.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-cset-shield.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "sessions-and-process-groups",
            "title": "Сеанси, групи процесів і керуючий термінал",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-job-control-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-shell-job-launch.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "preempt-rt",
            "title": "Гілка реального часу PREEMPT_RT",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-rt-lock-types.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-dual-kernel.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-rt-application.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "nohz-adaptive-tickless",
            "title": "Адаптивне ядро без тиків (NO_HZ_FULL)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "preempt-rt-architecture",
            "title": "Real-Time Linux patchset (PREEMPT_RT)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "deadline-scheduler",
            "title": "Планувальник SCHED_DEADLINE та алгоритм EDF",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "high-resolution-timers",
            "title": "Таймери високої точності (hrtimers)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "cgroups-v2-unified-hierarchy",
            "title": "Cgroups v2: єдина ієрархія",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "sched-ext-ebpf-scheduler",
            "title": "Планувальник sched_ext: eBPF розширення для sched",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sched-ext-ops.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-sched-ext.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-scx-simple-fifo.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "futex2-waitv-syscall",
            "title": "Багатооб’єктна синхронізація futex2 (sys_futex_waitv)",
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-futex-waitv.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-esync-fsync-futex2.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "cgroup-v2-memory-peak-swap",
            "title": "Управління піками та пропускною здатністю у Cgroups v2 memory",
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-memory-control-surface.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-cgroup-memory-monitor.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "sched-idle-and-sched-batch",
            "title": "Класи планирування SCHED_IDLE та SCHED_BATCH",
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sched-attr.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "sched-energy-aware-eas",
            "title": "Енергоефективне планування Energy-Aware Scheduling (EAS) та Energy Model",
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-energy-model-sysfs.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-eas-and-biglittle.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-eas-trace-analyzer.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-eas-cost-calculation.md",
                  "status": "done"
                }
              ]
            },
            "basic": {
              "status": "done"
            }
          },
          {
            "slug": "uclamp-utilization-clamping",
            "title": "Обмеження утилізації CPU: uclamp (sched_setattr uclamp_min/uclamp_max)",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-uclamp-kernel-structures.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-uclamp-and-pelt.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-uclamp-manager.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "sched-ext-custom-schedulers",
            "title": "Практична розробка BPF-планувальників у sched_ext (scx_rustland, scx_lavd)",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-scx-rust-framework.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-custom-schedulers.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-scx-lavd-deadline.md",
                  "status": "done"
                },
                {
                  "file": "proj-scx-rustland-architecture.md",
                  "status": "done"
                }
              ]
            }
          }
        ]
      },
      {
        "slug": "memory",
        "title": "Пам'ять процесу",
        "scope": "Віртуальна пам'ять як механізм: чому адреси брешуть і що з цього виходить.",
        "topics": [
          {
            "slug": "virtual-address-space",
            "title": "Віртуальний адресний простір процесу",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-maps-format.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-one-level-store.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-address-space-probe.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "paging-and-mmu",
            "title": "Сторінки, таблиці сторінок і MMU",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-pte-format.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-virt-to-phys.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-page-table-cost.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "page-fault",
            "title": "Сторінковий збій: чому все ліниве",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-fault-counters.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-demand-paging.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-fault-cost.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "mmap-model",
            "title": "mmap: файл і пам'ять як одне",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-mmap-flags.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-mmap-origin.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-mmap-vs-read.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "copy-on-write",
            "title": "Копіювання при записі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-cow-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-dirty-cow.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "swap-and-reclaim",
            "title": "Свопінг і витіснення сторінок",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-reclaim-counters.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-swapping-to-reclaim.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-observe-reclaim.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-thrashing-cliff.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "overcommit-and-oom",
            "title": "Overcommit і OOM-killer",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-oom-knobs.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-out-of-fuel.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-touch-the-promise.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "memory-accounting",
            "title": "Як міряти пам'ять процесу: VSZ, RSS, PSS",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-proc-memory-fields.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-pss-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-pss-by-hand.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "allocator-and-kernel",
            "title": "Звідки алокатор бере пам'ять: brk і mmap",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-mallopt-tunables.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-program-break.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-heap-probe.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "huge-pages",
            "title": "Великі сторінки: HugeTLB і прозорі великі сторінки",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-huge-page-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-huge-pages.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-huge-page-benchmark.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "address-space-randomization",
            "title": "Рандомізація адресного простору в системі: рівні та вимикачі",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-randomization-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-aslr-lineage.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-entropy-lab.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "userfaultfd",
            "title": "userfaultfd: сторінкові збої в руках програми",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-userfaultfd.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-userfaultfd.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-uffd-lazy-region.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-page-table-isolation",
            "title": "Ізоляція таблиць сторінок ядра (KPTI): чому ядро прибрали з простору процесу",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-pti-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-kaiser-to-kpti.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-kpti-cost.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "ksm-page-merging",
            "title": "KSM: злиття однакових сторінок",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-ksm-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-ksm-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-ksm-lab.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-memory-slab",
            "title": "Пам'ять ядра: slab і зменшувачі кешів",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-slab-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-slab-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-slab-watch.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "physical-page-allocator",
            "title": "Фізичні сторінки в ядрі: зони, блоки за порядками й ущільнення",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-allocator-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-buddy-and-fragmentation.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-buddyinfo-reader.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-fragmentation-index.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "memory-protection-keys",
            "title": "Ключі захисту пам'яті: PKU і PKRU",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-pkey-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-storage-keys.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-pkey-guard.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "vmalloc-kernel-mappings",
            "title": "vmalloc: віртуально суцільна пам'ять ядра",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-vmalloc-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-vmalloc-scalability.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-vmallocinfo-reader.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "reverse-mapping",
            "title": "Зворотне відображення сторінки (rmap): як знайти всіх, хто на неї вказує",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-rmap-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-anon-vma-war.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-who-maps-this-page.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "tlb-shootdown",
            "title": "Розсилання скидань TLB: чому правка таблиці сторінок коштує міжпроцесорних переривань",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-tlb-flush-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-shootdown-name.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-shootdown-cost.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "cma-contiguous-allocator",
            "title": "CMA: резерв суцільної фізичної пам'яті для пристроїв",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-cma-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-cma-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-cma-driver.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "page-pinning-gup",
            "title": "Закріплення сторінок для пристрою: get_user_pages і pin_user_pages",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-gup-family.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-gup-troubles.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-pin-user-buffer.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "memory-locking",
            "title": "Прибивання пам'яті: mlock, mlockall і сторінки, яких не можна віддати",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-locking-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-memlock-limit.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-realtime-preamble.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "memblock-early-memory",
            "title": "memblock: пам'ять до того, як з'явився розподільник сторінок",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-memblock-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-bootmem-to-memblock.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-read-memblock.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "mmu-notifiers",
            "title": "Сповіщувачі MMU: як драйвер дізнається, що ядро забирає сторінку",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-mmu-notifier-ops.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-mmu-notifier-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-mirror-a-range.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "sparsemem-and-vmemmap",
            "title": "Модель фізичної пам'яті: SPARSEMEM, vmemmap і масив описувачів кадрів",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sparsemem-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-memory-models.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-vmemmap-walk.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "hmm-address-space-mirroring",
            "title": "HMM: дзеркалення адресного простору процесу в пам'яті прискорювача",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-hmm-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-migrate-to-device.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "cgroup-writeback",
            "title": "Фоновий запис по cgroup: чия брудна сторінка й хто платить за її злив",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-cgwb-contract.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-one-owner-per-inode.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-whose-write-is-it.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "memory-hotplug",
            "title": "Гаряче додавання й вилучення пам'яті: секції, блоки й перехід в онлайн",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "page-migration",
            "title": "Міграція сторінок: перенести вміст в інший кадр, не зламавши посилань",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-move-pages.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "memory-failure-hwpoison",
            "title": "Апаратна помилка пам'яті: hwpoison, SIGBUS і отруєна сторінка",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-hwpoison-interfaces.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-sigbus-handler.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "asynchronous-page-reclaim",
            "title": "Асинхронне витіснення сторінок: kswapd та watermarks",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          }
        ]
      },
      {
        "slug": "files",
        "title": "Файли й файлові системи",
        "scope": "Що таке файл у Unix, як імена відв'язані від вмісту й на чому тримається узгодженість.",
        "topics": [
          { slug: "file-descriptors-and-open-file-table", title: "file-descriptors-and-open-file-table", basic: { status: "empty" }, detailed: { status: "done" } },
          { slug: "extended-attributes-xattr", title: "extended-attributes-xattr", basic: { status: "empty" }, detailed: { status: "done" } },
          {
            "slug": "file-descriptor",
            "title": "Файловий дескриптор",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-fd-lifecycle.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-fd-origin.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-fd-table-tour.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "open-file-description",
            "title": "Опис відкритого файлу: що спільне після fork",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-fd-vs-ofd.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-file-table.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-shared-offset.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "inode-model",
            "title": "Inode: файл без імені",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-stat-fields.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-i-number.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-inode-identity.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "directory-as-mapping",
            "title": "Каталог як відображення імен",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-directory-syscalls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-directory-formats.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-walk-directory.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "hard-and-symbolic-links",
            "title": "Жорсткі й символьні посилання",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-link-syscalls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-symlink-arrival.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-two-counters.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "path-resolution",
            "title": "Розбір шляху",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-resolution-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-namei.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-resolve-by-hand.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "vfs-layer",
            "title": "VFS: спільний шар над файловими системами",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-vfs-operation-tables.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-vnode-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-minimal-filesystem-module.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "mount-model",
            "title": "Монтування й дерево монтувань",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-mount-syscalls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-mount-lineage.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-mountinfo-tree.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "filesystem-families",
            "title": "Родини файлових систем: ext4, XFS, Btrfs, F2FS",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-mkfs-and-mount.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-four-births.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-fiemap-layout.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "journaling-consistency",
            "title": "Журналювання й узгодженість після збою",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-journal-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-fsck-to-journal.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-journal-replay.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "page-cache-durability",
            "title": "Кеш сторінок, fsync і довговічність запису",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sync-syscalls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-o-ponies.md",
                  "status": "done"
                },
                {
                  "file": "hist-fsyncgate.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-durable-write.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "pseudo-filesystems",
            "title": "Псевдо-ФС: procfs, sysfs, tmpfs, devtmpfs",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-proc-origin.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-seqfile-module.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "fuse-userspace-filesystems",
            "title": "FUSE: файлова система в просторі користувача",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-fuse-protocol.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-fuse-origins.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-hello-fuse.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "sparse-files",
            "title": "Розріджені файли: діри замість нулів",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sparse-syscalls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-seek-hole.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-hole-map.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "chroot",
            "title": "chroot і його межі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-chroot-contract.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-chroot-origins.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-escape-demo.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "network-filesystems",
            "title": "Мережеві файлові системи: NFS, SMB і чого від них чекати",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-mount-options.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-nfs-and-smb-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-mount-contract-probe.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "file-locking",
            "title": "Блокування файлів: flock, POSIX-замки й замки на опис відкритого файлу",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-lock-interfaces.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-file-lock.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "at-family-syscalls",
            "title": "Сімейство *at: шлях, відлічений від дескриптора каталогу",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-at-family-reference.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-at-family-origin.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "reflink-copies",
            "title": "Копії з поділом блоків: reflink і copy_file_range",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-clone-and-copy.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-reflink-syscall.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-dedupe-ranges.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "readahead",
            "title": "Випереджувальне читання: як ядро вгадує наступний блок",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-readahead-lineage.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-measure-readahead.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-window-and-bandwidth.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "overlay-filesystems",
            "title": "Накладені файлові системи: overlayfs, шари й «білило»",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-overlay-mount.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-union-mounts.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-overlay-lab.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "statx-extended-stat",
            "title": "statx: розширений запит атрибутів файлу",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-seven-years-to-statx.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-capability-survey.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "large-file-support",
            "title": "Великі файли: off_t, LFS і _FILE_OFFSET_BITS",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-lfs-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-large-file-summit.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-offset-audit.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "fsck-and-repair",
            "title": "fsck: перевірка й ремонт файлової системи",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-fsck-invocation.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-linkcount-audit.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "pivot-root",
            "title": "pivot_root: підміна кореневого монтування",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-pivot-root-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-detached-root-probe.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "inotify-and-fanotify",
            "title": "Стеження за змінами у файловій системі: inotify і fanotify",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-notify-syscalls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-dnotify-to-fanotify.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-watch-tree.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "log-structured-filesystems",
            "title": "Лог-структуровані файлові системи",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-f2fs-ioctls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-lfs-argument.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-segment-cleaner.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-cleaning-cost.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "file-leases",
            "title": "Оренда файлу: F_SETLEASE і сповіщення про чуже відкриття",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-lease-interface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-oplocks-and-delegations.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-lease-holder.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "file-block-allocation",
            "title": "Розміщення блоків файлу: екстенти, відкладене виділення й фрагментація",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-allocation-controls.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-allocator-lab.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-fragmentation-cost.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "read-only-image-filesystems",
            "title": "Стиснені образи лише для читання: SquashFS і EROFS",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-two-births.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-image-lab.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-block-size-tradeoff.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "file-handles",
            "title": "Стійке посилання на файл: name_to_handle_at і open_by_handle_at",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-handle-syscalls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-nfs-handle-lineage.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-handle-index.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "fs-verity",
            "title": "fs-verity: перевірка вмісту файлу на читанні",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-fsverity-ioctls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-two-apis.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-recompute-digest.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "o-tmpfile",
            "title": "O_TMPFILE: безіменний файл на справжній файловій системі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-temp-file-races.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-atomic-publish.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "inode-flags-chattr",
            "title": "Прапорці inode: immutable, append-only й chattr",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-fileattr-interface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-immutable-lineage.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-flag-tour.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "disk-quotas",
            "title": "Дискові квоти: облік місця за власником",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-quota-control.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-quota-birth.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "filesystem-freeze",
            "title": "Заморожування файлової системи: узгоджений момент для знімка",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-freeze-interface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-xfs-to-fifreeze.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-freeze-window.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "fscrypt",
            "title": "fscrypt: шифрування на рівні файлової системи",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-fscrypt-ioctls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-ecryptfs-to-fbe.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-derive-file-key.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "configfs",
            "title": "configfs: об'єкти ядра, які створює простір користувача",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-configfs-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-configfs-module.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "dax-direct-access",
            "title": "DAX: пряме звертання до файлів на постійній пам'яті",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-dax-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-xip-to-dax.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-persist-by-hand.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "virtiofs",
            "title": "virtiofs: каталог хоста у віртуальній машині через спільну пам'ять",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-virtiofs-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-9p-to-virtiofs.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-count-the-crossings.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "zonefs",
            "title": "zonefs: кожна зона носія як звичайний файл",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-zonefs-surface.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-append-to-zone-file.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "device-mapper-dm-crypt",
            "title": "Device Mapper: LVM, DM-Crypt та LUKS",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "btrfs-copy-on-write-and-subvolumes",
            "title": "Btrfs: Copy-on-Write, Субтоми та Знімки",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-btrfs-subvol-ioctls.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-btrfs-subvolumes.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-snapshot-manager.md",
                "status": "done",
            "api": [
              {
                "file": "api-btrfs-subvol-ioctls.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-btrfs-subvolumes.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-snapshot-manager.md",
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
              "status": "done"
            }
          },
          {
            "slug": "btrfs-b-tree-architecture",
            "title": "Btrfs: Архітектура B-дерев",
            "basic": {
              "status": "done",
            "api": [
              {
                "file": "api-btrfs-tree-types.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-btrfs-creation.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-btrfs-key-search.md",
                "status": "done",
            "api": [
              {
                "file": "api-btrfs-tree-types.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-btrfs-creation.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-btrfs-key-search.md",
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
              "status": "done",
              "api": [
                {
                  "file": "api-btrfs-tree-types.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-btrfs-creation.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-btrfs-key-search.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "btrfs-checksums-scrubbing-raid",
            "title": "Btrfs: Контрольні суми, Scrubbing та RAID",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-btrfs-scrub-ioctl.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-silent-data-corruption.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-crc32c-btrfs.md",
                "status": "done",
            "api": [
              {
                "file": "api-btrfs-scrub-ioctl.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-silent-data-corruption.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-crc32c-btrfs.md",
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
              "status": "done",
              "api": [
                {
                  "file": "api-btrfs-scrub-ioctl.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-silent-data-corruption.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-crc32c-btrfs.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "zfs-on-linux-arc",
            "title": "ZFS у Linux: ARC кеш та ZIL",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-arc-kstat.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-arc-algorithm.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-arc-monitoring.md",
                "status": "done",
            "api": [
              {
                "file": "api-arc-kstat.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-arc-algorithm.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-arc-monitoring.md",
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
              "status": "done"
            }
          },
          {
            "slug": "zfs-native-encryption",
            "title": "Вбудоване шифрування та дедуплікація в ZFS",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-zfs-crypto-cli.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-zfs-key-manager.md",
                "status": "done",
            "api": [
              {
                "file": "api-zfs-crypto-cli.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-zfs-key-manager.md",
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
          },
          {
            "slug": "erofs-read-only-filesystem",
            "title": "Стиснена файлова система EROFS для контейнерів та прошивок",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-erofs-ondisk.md",
                "status": "done",
            "comp": [
              {
                "file": "comp-squashfs-vs-erofs.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-erofs-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-erofs-toolchain.md",
                "status": "done",
            "api": [
              {
                "file": "api-erofs-ondisk.md",
                "status": "done",
            "comp": [
              {
                "file": "comp-squashfs-vs-erofs.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-erofs-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-erofs-toolchain.md",
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
            }
          },
          {
            "slug": "statx-extended-stat-api",
            "title": "Розширений системний виклик statx та маски атрибутів",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-statx-masks-and-flags.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-statx-inspect.md",
                "status": "done",
            "api": [
              {
                "file": "api-statx-masks-and-flags.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-statx-inspect.md",
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
          },
          {
            "slug": "copy-file-range-syscall",
            "title": "Системний виклик copy_file_range(2) та server-side copy",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-copy-file-range-spec.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-copy-engine.md",
                "status": "done",
            "api": [
              {
                "file": "api-copy-file-range-spec.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-copy-engine.md",
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
          },
          {
            "slug": "pidfs-filesystem-architecture",
            "title": "Спеціалізована файлова система pidfs у сучасних ядрах",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-pidfs-ioctls.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-pid-recycling-to-pidfs.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-pidfs-identity-checker.md",
                "status": "done",
            "api": [
              {
                "file": "api-pidfs-ioctls.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-pid-recycling-to-pidfs.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-pidfs-identity-checker.md",
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
          },
          {
            "slug": "incfs-incremental-filesystem",
            "title": "Інкрементальна файлова система IncFS (Android Incremental Delivery)",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-incfs-ctl.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-android-incremental.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-incfs-daemon.md",
                "status": "done",
            "api": [
              {
                "file": "api-incfs-ctl.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-android-incremental.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-incfs-daemon.md",
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
          },
          {
            "slug": "fanotify-fsnotify-permission-events",
            "title": "Розширений моніторинг файлів fanotify: перехоплення FAN_OPEN_PERM",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-fanotify-perm-reference.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-fsnotify-perm-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-fanotify-guard.md",
                "status": "done",
            "api": [
              {
                "file": "api-fanotify-perm-reference.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-fsnotify-perm-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-fanotify-guard.md",
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
          },
          {
            "slug": "zfs-pool-architecture",
            "title": "Архітектура пулів ZFS: від дисків до наборів даних",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-zfs-pool-management.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-zfs-architecture-birth.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-zfs-block-pointer-parser.md",
                "status": "done",
            "api": [
              {
                "file": "api-zfs-pool-management.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-zfs-architecture-birth.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-zfs-block-pointer-parser.md",
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
              "status": "done"
            }
          }
        ]
      },
      {
        "slug": "io",
        "title": "Ввід-вивід і очікування",
        "scope": "Як програма чекає на дані й чому саме тут вирішується, скільки з'єднань вона потягне.",
        "topics": [
          { slug: "readdir-getdents64-directory-traversal", title: "Обхід каталогів: readdir, getdents64 та внутрішня структура", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-getdents64-structs.md", status: "done" }] , "hist": [{ file: "hist-readdir-r-deprecation.md", status: "done" }] , "proj": [{ file: "proj-fast-directory-walker.md", status: "done" }] },
          { slug: "fsync-fdatasync-sync-file-range", title: "Гарантії скидання кешу: fsync, fdatasync та sync_file_range", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-sync-contracts.md", status: "done" }] , "hist": [{ file: "hist-fsyncgate-and-cache.md", status: "done" }] , "proj": [{ file: "proj-sync-bench.md", status: "done" }] },
          { slug: "copy-file-range-cross-fs-reflink", title: "copy_file_range, reflink та копіювання на рівні ФС", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-cross-fs-matrix.md", status: "done" }] , "hist": [{ file: "hist-cross-fs-evolution.md", status: "done" }] , "proj": [{ file: "proj-cross-fs-cloner.md", status: "done" }] },
          { slug: "dma-mapping-subsystem-and-iommu", title: "Підсистема DMA mapping та IOMMU в ядрі Linux", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-dma-mapping-surface.md", status: "done" }] , "hist": [{ file: "hist-dma-evolution.md", status: "done" }] , "proj": [{ file: "proj-dma-driver-example.md", status: "done" }] },
          {
            "slug": "zoned-storage-f2fs-integration",
            "title": "Файлова система f2fs для зонованих пристроїв ZNS",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-zns-f2fs-interfaces.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-from-ftl-to-zns.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-zns-zone-append.md",
                "status": "done",
            "api": [
              {
                "file": "api-zns-f2fs-interfaces.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-from-ftl-to-zns.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-zns-zone-append.md",
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
              "status": "done"
            }
          },
          {
            "slug": "blocking-and-nonblocking",
            "title": "Блокуючий і неблокуючий режим",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-nonblock-contract.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-ndelay-to-nonblock.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-echo-two-ways.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "readiness-vs-completion",
            "title": "Готовність проти завершення: дві моделі вводу-виводу",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-two-lineages.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-two-models-one-server.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "select-poll-epoll",
            "title": "select, poll, epoll: чекати на багато джерел",
            "basic": {
              "status": "done",
            "api": [
              {
                "file": "api-epoll-interfaces.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-c10k.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-scaling-measure.md",
                "status": "done",
            "api": [
              {
                "file": "api-epoll-interfaces.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-c10k.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-scaling-measure.md",
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
              "status": "done",
              "api": [
                {
                  "file": "api-epoll-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-c10k.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-scaling-measure.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "io-uring",
            "title": "io_uring: кільця подань і завершень",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-uring-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-aio-to-uring.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-uring-echo.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "unix-domain-sockets",
            "title": "Сокети домену Unix і передача дескрипторів",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-ancillary-data.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-pass-a-descriptor.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "socket-as-descriptor",
            "title": "Сокет як дескриптор",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-socket-or-file.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-connection-budget.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "buffered-and-direct-io",
            "title": "Буферизований і прямий ввід-вивід",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-direct-io-contract.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-o-direct-arrival.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-direct-copy.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "zero-copy",
            "title": "Передача без копіювання: sendfile і splice",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-transfer-calls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-sendfile-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-sendfile-server.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "eintr-and-restart",
            "title": "EINTR: перервані виклики й перезапуск",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-restart-matrix.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-restart-wars.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-retry-right.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "stdio-buffering",
            "title": "Буферизація stdio: порядкова, поблокова, без буфера",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-stdio-buffer-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-lesk-and-ritchie.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-buffering-lab.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "signal-driven-io",
            "title": "Ввід-вивід за сигналом: F_SETOWN, F_SETSIG і SIGIO",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-signal-io-contract.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-sigio-lineage.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-signal-driven-echo.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "posix-aio",
            "title": "POSIX AIO: стандартний інтерфейс aio_*",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-aio-calls.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-aio-file-reader.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "linux-aio-io-submit",
            "title": "Асинхронний ввід-вивід ядра: io_submit і його межі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-aio-syscalls.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-direct-read-depth.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "io-priorities",
            "title": "Пріоритет вводу-виводу: класи ionice та ioprio_set",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-ioprio.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-ioprio-and-cfq.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-does-ionice-work.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "io-uring-architecture",
            "title": "Сучасний асинхронний ввід-вивід io_uring",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-liburing-ring.md",
                "status": "done",
            "api": [
              {
                "file": "api-liburing-ring.md",
                "status": "done"
              }
            ],
              }
            ],
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "block-layer-mq",
            "title": "Багаточергова підсистема блокового вводу-виводу (blk-mq)",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-blk-mq-sysfs-and-trace.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-single-queue-to-blk-mq.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-null-blk-benchmark.md",
                "status": "done",
            "api": [
              {
                "file": "api-blk-mq-sysfs-and-trace.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-single-queue-to-blk-mq.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-null-blk-benchmark.md",
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
              "status": "done"
            }
          },
          {
            "slug": "ublk-userspace-block-driver",
            "title": "Фреймворк ublk: блокові драйвери у просторі користувача",
              "basic": {
                "status": "done",
            "hist": [
              {
                "file": "hist-userspace-block-devs.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-ublk-target.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-userspace-block-devs.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-ublk-target.md",
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
              "status": "done"
            }
          },
          {
            "slug": "zoned-block-devices-zns",
            "title": "Зоновані блокові пристрої (ZBC/ZAC та zonefs)",
              "basic": {
                "status": "done",
            "api": [
              {
                "file": "api-zbd-ioctls.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-smr-to-zns.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-zone-append-demo.md",
                "status": "done",
            "api": [
              {
                "file": "api-zbd-ioctls.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-smr-to-zns.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-zone-append-demo.md",
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
              "status": "done"
            }
          },
          {
            "slug": "zoned-storage-f2fs-integration",
            "title": "Файлова система f2fs для зонованих пристроїв ZNS",
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "dm-writecache-and-dm-cache",
            "title": "Кешування блокових пристроїв: dm-writecache та dm-cache",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-dm-target-parameters-and-status.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-block-caching-in-linux.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-dm-cache-status-monitor.md",
                "status": "done",
            "api": [
              {
                "file": "api-dm-target-parameters-and-status.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-block-caching-in-linux.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-dm-cache-status-monitor.md",
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
          },
          {
            "slug": "blk-iopoll-and-io-polling",
            "title": "Опитування блокових пристроїв: IO polling та blk-mq iopoll",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-iopoll-sysfs-params.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-polling-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-hipri-bench.md",
                "status": "done",
            "api": [
              {
                "file": "api-iopoll-sysfs-params.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-polling-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-hipri-bench.md",
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
          },
          {
            "slug": "nvme-target-kernel-subsystem",
            "title": "Підсистема NVMe Target (nvmet) у ядрі Linux",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-nvmet-ops.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-target-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-nvmet-c-cpp-configfs.md",
                "status": "done",
            "api": [
              {
                "file": "api-nvmet-ops.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-target-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-nvmet-c-cpp-configfs.md",
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
          },
          {
            "slug": "blk-mq-tag-sets-and-hardware-queues",
            "title": "Слоти команд у blk-mq: Tag Sets та Hardware Dispatch Queues",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-blk-mq-tag-set-surface.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-sbitmap-allocator.md",
                "status": "done",
            "api": [
              {
                "file": "api-blk-mq-tag-set-surface.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-sbitmap-allocator.md",
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
          },
          {
            "slug": "dma-buf-heaps-framework",
            "title": "Фреймворк dma-buf heaps: заміна ION для виділення неперервної памʼяті",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-uapi-dma-heap.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-zerocopy-pipeline.md",
                "status": "done",
            "api": [
              {
                "file": "api-uapi-dma-heap.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-zerocopy-pipeline.md",
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
          },
          {
            "slug": "io-uring-cmd-passthrough",
            "title": "Низькорівневий пасстру команд NVMe через IORING_OP_URING_CMD",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-uring-cmd-nvme.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-nvme-passthrough-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-nvme-passthrough-bench.md",
                "status": "done",
            "api": [
              {
                "file": "api-uring-cmd-nvme.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-nvme-passthrough-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-nvme-passthrough-bench.md",
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
          }
        ]
      },
      {
        "slug": "signals-ipc",
        "title": "Сигнали й взаємодія процесів",
        "scope": "Асинхронні сповіщення та способи, якими процеси домовляються між собою.",
        "topics": [
          { slug: "signal-architecture-and-delivery", title: "Архітектура та доставка сигналів", basic: { status: "empty" }, detailed: { status: "done" } },
          {
            "slug": "signal-model",
            "title": "Сигнал: асинхронне сповіщення",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sending-signals.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-unreliable-signals.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-signal-race.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "signal-disposition",
            "title": "Диспозиція сигналу: обробник, ігнорування, типова дія",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sigaction.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-unreliable-signals.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "async-signal-safety",
            "title": "Що взагалі можна робити в обробнику сигналу",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-safe-functions.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-signal-to-event-loop.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "signal-mask-signalfd",
            "title": "Маскування сигналів і signalfd",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-signal-mask-and-signalfd.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-self-pipe-to-signalfd.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-signalfd-supervisor.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "ipc-landscape",
            "title": "Огляд засобів взаємодії: що коли обирати",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-ipc-comparison.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-sysv-and-posix-ipc.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-ipc-latency-bench.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "posix-shared-memory",
            "title": "Спільна пам'ять POSIX",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-sysv-vs-posix.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-shm-ring.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "message-queues",
            "title": "Черги повідомлень",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-message-queues.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-priority-dispatcher.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "eventfd-and-futex",
            "title": "eventfd і futex: сповіщення й дешеве очікування",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-futex-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-futex-mutex.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "process-timers",
            "title": "Таймери процесу: alarm, setitimer, POSIX-таймери й timerfd",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-timer-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-alarm-to-timerfd.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-timerfd-scheduler.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "signal-frame-and-sigreturn",
            "title": "Сигнальний кадр і повернення з обробника (rt_sigreturn)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-signal-frame-layout.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-trampoline-on-the-stack.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-context-rewrite.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "realtime-signals",
            "title": "Реальночасові сигнали: черга, порядок доставки й siginfo",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-realtime-signals.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-rt-signal-dispatch.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "dbus",
            "title": "D-Bus: шина повідомлень простору користувача",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-dbus-wire.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-dbus-origin.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-dbus-service.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "memfd-create",
            "title": "memfd_create: безіменний файл у пам'яті й пломби (seals)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-memfd-and-seals.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-sealing-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-sealed-buffer.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "process-shared-sync",
            "title": "Синхронізація між процесами: POSIX-семафори й спільні м'ютекси",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-process-shared-sync.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-shared-work-queue.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "posix-semaphores",
            "title": "Семафори POSIX: іменовані й безіменні",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-dijkstra-semaphore.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-producer-consumer.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "pipe-and-fifo",
            "title": "Канали й іменовані канали",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-pipe-fifo.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-pipe-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-pipeline-by-hand.md",
                  "status": "done"
                }
              ]
            }
          }
        ]
      },
      {
        "slug": "permissions",
        "title": "Права й ідентичність",
        "scope": "Хто такий процес з погляду системи і як вирішується, що йому дозволено.",
        "topics": [
          { slug: "seccomp-syscall-filtering", title: "Գ�������� ��������� ������� (seccomp)", basic: { status: "done" }, detailed: { status: "done" } },
          { slug: "capabilities-in-practice", title: "Можливості на практиці: файли, процеси та systemd", basic: { status: "done" }, detailed: { status: "done" } },
          {
            "slug": "uid-gid-model",
            "title": "Користувачі, групи й ідентичність процесу",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-credential-syscalls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-setuid-semantics.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-drop-privileges.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "process-credentials-uids-gids",
            "title": "Креденшели процесів: Real, Effective, Saved UID/GID",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-cred-syscalls.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-posix-credentials.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-privilege-drop.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "permission-bits",
            "title": "Біти прав і як їх перевіряють",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-mode-bits.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-nine-bits.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-access-check.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "setuid-and-privilege",
            "title": "setuid, setgid і підвищення прав",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-environment-holes.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-setuid-helper.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "umask-and-defaults",
            "title": "umask і типові права новоствореного",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-umask-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-umask-origin.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-exact-mode.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "capabilities",
            "title": "Можливості (capabilities) замість всесильного root",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-capability-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-posix-1e.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-keep-capability.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "acl-and-xattr",
            "title": "Розширені права (ACL) і атрибути (xattr)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-xattr-and-acl.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-withdrawn-draft.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-decode-acl-blob.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "mac-selinux-apparmor",
            "title": "Обов'язковий контроль доступу: SELinux і AppArmor",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-selinux-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-mac-in-linux.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-denial-to-policy.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "device-access-groups",
            "title": "Доступ до пристроїв через групи: dialout, plugdev",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-udev-access-rules.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-dialout-uucp.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "seccomp-filtering",
            "title": "seccomp: фільтрація системних викликів",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-seccomp.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-seccomp-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-seccomp-filter.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "pam-stack",
            "title": "PAM: стек модулів автентифікації",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-pam-config.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-pam-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-pam-module.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-keyrings",
            "title": "Кільця ключів ядра: add_key, keyctl і довірені сертифікати",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-keyctl-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-key-service-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-key-possession.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "ima-appraisal",
            "title": "IMA: вимірювання й оцінка цілісності файлів у ядрі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-ima-policy.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-ima-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-replay-measurements.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "privilege-separation",
            "title": "Розділення привілеїв: маленький довірений процес і решта",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-privsep-origins.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-privsep-helper.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "polkit",
            "title": "polkit: хто дозволяє непривілейованому процесу привілейовану дію",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-polkit-files.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-policykit-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-polkit-mechanism.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "user-database-nss",
            "title": "База облікових записів: passwd, group, shadow і шар NSS",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-nsswitch-and-getent.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-shadow-and-nis.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-nss-module.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "lsm-framework",
            "title": "LSM: каркас гачків безпеки в ядрі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-lsm-module.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-restrictive-hooks.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-bpf-lsm.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "landlock",
            "title": "Landlock: непривілейоване обмеження доступу до файлів",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-landlock-syscalls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-landlock-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-sandbox-exec.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "ldap-directory",
            "title": "Каталог LDAP як мережеве джерело облікових записів",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-ldap-search-and-schema.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-x500-to-ldap.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-ldap-login-check.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "sudo",
            "title": "sudo: підвищення прав за правилами sudoers",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sudoers-syntax.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-sudo-lineage.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-sudo-wrapper.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "userdb-varlink",
            "title": "userdb: облікові записи як записи JSON через Varlink",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-userdb-varlink.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-varlink-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-userdb-service.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "sssd",
            "title": "SSSD: демон, що тримає з'єднання з каталогом і кеш облікових записів",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sssd-config-and-tools.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-sssd-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-measure-cache.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "su-switch-user",
            "title": "su: перемикання на іншого користувача",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-su-invocation.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-su-and-wheel.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-minimal-su.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "systemd-homed",
            "title": "systemd-homed: домівка як переносний підписаний образ",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-homectl-and-record.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-homed-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-inspect-home-image.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-lockdown",
            "title": "Режим блокування ядра (lockdown): чого не можна навіть root",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-lockdown-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-lockdown-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-probe-lockdown.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "selinux-type-enforcement",
            "title": "SELinux: Type Enforcement та контексти безпеки",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-selinuxfs-interface.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-flask-architecture.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-te-policy-module.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "apparmor-path-rules",
            "title": "AppArmor: профілі на основі шляхів",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-apparmor-rule-syntax.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-apparmor-pathname-lsm.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-apparmor-securityfs-interface.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "landlock-unprivileged-sandboxing",
            "title": "Landlock LSM: безпривілейоване обмеження файлового доступу",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "seccomp-bpf-filtering",
            "title": "Фільтрація системних викликів Seccomp-BPF",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-seccomp-syscall.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-seccomp-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-custom-seccomp.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "lsm-stacking-framework",
            "title": "Каркас модулів безпеки Linux (LSM Hooks)",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-lsm-kernel-interface.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-stacking-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-lsm-blob-offset.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "kernel-keyring-subsystem",
            "title": "Підсистема ключів ядра (Kernel Keyring)",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-key-retention-structures.md",
                "status": "done"
              }
            ],
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "kernel-crypto-framework",
            "title": "Криптографічний API ядра (Kernel Crypto API)",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-af-alg.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-ipsec-crypto-birth.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-af-alg-crypto.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "pam-authentication-stack",
            "title": "Платформа авторизації PAM",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-pam-library-contract.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-sun-openpam.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-custom-pam-module.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "user-namespaces-uid-mapping",
            "title": "Юзер-простори імен (User Namespaces)",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-userns-procfs.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-rootless-and-userns.md",
                "status": "done",
            "math": [
              {
                "file": "math-uid-translation.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-uid-mapping-helper.md",
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
              "status": "done"
            }
          },
          {
            "slug": "rootless-containers",
            "title": "Безкорінна контейнеризація",
            "basic": {
              "status": "done",
            "api": [
              {
                "file": "api-subuid-and-newuidmap.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-rootless-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-rootless-ns-setup.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "ebpf-lsm-custom-policies",
            "title": "Програмовані політики безпеки BPF-LSM",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-bpf-lsm-hooks.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-bpf-lsm-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-bpf-lsm-loader.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            }
          },
          {
            "slug": "ebpf-security-tracing",
            "title": "eBPF у безпеці та трасуванні",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-bpf-helpers-tracing.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-auditd-to-ebpf.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-ebpf-exec-monitor.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "ima-evm-integrity-architecture",
            "title": "Вимірювання цілісності системи: IMA та EVM",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-evm-xattr-format.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-evm-tpm-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-inspect-ima-evm.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            },
            "basic": {
              "status": "done"
            }
          },
          {
            "slug": "tpm2-software-stack",
            "title": "Стек TPM 2.0 та апаратне зберігання ключів",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-tss2-esapi.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-tpm-12-to-20.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-tpm2-esys-unseal.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            }
          },
          {
            "slug": "sigstruct-and-sgx-enclaves",
            "title": "Апаратні енклави Intel SGX та сигнатури SIGSTRUCT",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-sigstruct.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-launch-control-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-enclave-loader.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            }
          },
          {
            "slug": "kernel-lockdown-integrity",
            "title": "Режим мажоритарного захисту ядра: Kernel Lockdown Mode",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-lockdown-reasons.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-lockdown-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-check-lockdown.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            }
          },
          {
            "slug": "landlock-abi-v4-v5-features",
            "title": "Еволюція Landlock LSM: ABI v4/v5 (мережеві обмеження та ioctl)",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-landlock-v4-v5-structs.md",
                "status": "done",
            "comp": [
              {
                "file": "comp-landlock-vs-seccomp-apparmor.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-landlock-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-landlock-network-ioctl-sandbox.md",
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
          },
          {
            "slug": "apparmor-stacking-and-profiles",
            "title": "Стек профілів AppArmor та інстанціація політик",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-apparmor-stacking-interface.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-apparmor-stacking-evolution.md",
                "status": "done",
            "math": [
              {
                "file": "math-stacking-intersection.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-apparmor-policy-instantiation.md",
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
          },
          {
            "slug": "tomoyo-linux-path-based-lsm",
            "title": "Політики безпеки TOMOYO Linux: LSM на основі шляхів",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-tomoyo-policy-syntax.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-tomoyo-pathname-mac.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-tomoyo-policy-editor.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            }
          },
          {
            "slug": "smack-simplified-mandatory-access",
            "title": "Спрощений мандатний контроль доступу SMACK (Simplified Mandatory Access Control)",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-smackfs-and-xattr.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-smack-creation.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-smack-policy-loader.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            }
          },
          {
            "slug": "bpf-lsm-audit-and-override",
            "title": "Модифікація поведінки Security Modules через bpf_lsm (bpf_override_return)",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-bpf-lsm-helpers.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-bpf-lsm-override.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-bpf-lsm-override.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            }
          }
        ]
      },
      {
        "slug": "devices",
        "title": "Пристрої та ядро",
        "scope": "Як залізо стає файлом і як ядро керує тим, що під'єднали.",
        "topics": [
          { slug: "nvme-over-fabrics-nvme-of", title: "Мережевий доступ до блочних пристроїв NVMe over Fabrics (RDMA/TCP)", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-nvmeof-pdu-structures.md", status: "done" }] , "hist": [{ file: "hist-iscsi-to-nvmeof.md", status: "done" }] , "math": [{ file: "math-nvmeof-latency-throughput.md", status: "done" }] , "proj": [{ file: "proj-nvmeof-c-cpp-client.md", status: "done" }] },
          { slug: "gpio-descriptor-based-gpiod-api", title: "Ядерний дескрипторний API gpiod (gpiod_get, gpiod_set_value)", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-kernel-gpiod-functions.md", status: "done" }] , "hist": [{ file: "hist-legacy-gpio-to-gpiod.md", status: "done" }] , "proj": [{ file: "proj-kernel-gpio-driver.md", status: "done" }] },
          { slug: "devicetree-overlays-and-dtbo", title: "devicetree-overlays-and-dtbo", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-dtbo-kernel-interfaces.md", status: "done" }] , "hist": [{ file: "hist-dtbo-evolution.md", status: "done" }] , "proj": [{ file: "proj-dtbo-configfs-loader.md", status: "done" }] },
          { slug: "usb-type-c-connector-class-framework", title: "Фреймворк коннекторів USB Type-C та Power Delivery", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-typec-kernel-sysfs.md", status: "done" }] , "comp": [{ file: "comp-tcpm-tcpci-ucsi.md", status: "done" }] , "hist": [{ file: "hist-typec-pd-evolution.md", status: "done" }] , "proj": [{ file: "proj-typec-role-switcher.md", status: "done" }] },
          { slug: "input-event-codes-and-evdev", title: "Підсистема введення та події evdev (/dev/input/eventN)", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-evdev-ioctl.md", status: "done" }] , "hist": [{ file: "hist-linux-input-subsystem.md", status: "done" }] , "math": [{ file: "math-evdev-abs-scaling.md", status: "done" }] , "proj": [{ file: "proj-evdev-event-loop.md", status: "done" }] },
          { slug: "gpio-character-device-v2", title: "Сучасний інтерфейс GPIO chardev ABI v2 (/dev/gpiochipN)", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-v2-structures-and-ioctls.md", status: "done" }] , "hist": [{ file: "hist-abi-v1-vs-v2.md", status: "done" }] , "proj": [{ file: "proj-v2-raw-ioctl-and-libgpiod.md", status: "done" }] },
          { slug: "power-management-qos-framework", title: "PM QoS: фреймворк гарантій продуктивності та управління затримками в ядрі Linux", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-pm-qos-kernel.md", status: "done" }] , "hist": [{ file: "hist-pm-qos-evolution.md", status: "done" }] , "proj": [{ file: "proj-pm-qos-benchmark.md", status: "done" }] },
          { slug: "v4l2-media-subsystem", title: "Підсистема відео та медіа-пристроїв (V4L2, Media Controller)", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-v4l2-mc-core.md", status: "done" }] , "hist": [{ file: "hist-v4l1-to-media-controller.md", status: "done" }] , "math": [{ file: "math-media-pipeline-bandwidth.md", status: "done" }] , "proj": [{ file: "proj-v4l2-capture.md", status: "done" }] },
          { slug: "virtio-mem-and-virtio-pmem", title: "Динамічне додавання пам'яті: virtio-mem та virtio-pmem", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-virtio-mem-spec.md", status: "done" }] , "comp": [{ file: "comp-virtio-mem-vs-acpi-dimm.md", status: "done" }] , "hist": [{ file: "hist-virtio-mem-genesis.md", status: "done" }] , "proj": [{ file: "proj-virtio-mem-driver.md", status: "done" }] },
          { slug: "watchdog-timer-subsystem", title: "Підсистема та драйвери таймерів Watchdog (/dev/watchdog)", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-watchdog-ioctl-abi.md", status: "done" }] , "comp": [{ file: "comp-hardware-watchdog-architecture.md", status: "done" }] , "hist": [{ file: "hist-watchdog-evolution.md", status: "done" }] , "math": [{ file: "math-watchdog-timeout-window.md", status: "done" }] , "proj": [{ file: "proj-watchdog-daemon.md", status: "done" }] },
          { slug: "character-and-block-devices", title: "Символьні та блочні пристрої", basic: { status: "done" }, detailed: { status: "done" } , "api": [{ file: "api-cdev-bdev-interfaces.md", status: "done" }] , "hist": [{ file: "hist-raw-devices-and-devfs.md", status: "done" }] , "proj": [{ file: "proj-cdev-bdev-userspace.md", status: "done" }] },
          {
            "slug": "procfs-process-reflection",
            "title": "Відображення процесів у procfs",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-procfs-process-layout.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-procfs-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-procfs-inspector.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "device-file-model",
            "title": "Файл пристрою: символьний і блоковий",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-dev-directory.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-char-driver.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "major-minor-numbers",
            "title": "Старший і молодший номери пристрою",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-dev-numbers.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-number-space.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-minor-fanout.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "sysfs-device-model",
            "title": "Модель пристроїв у sysfs",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sysfs-tree.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-driver-model-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-sysfs-attribute-module.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "udev-rules",
            "title": "udev: іменування пристроїв і правила",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-rule-keys.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-udev-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-hotplug-service.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-modules",
            "title": "Модулі ядра: завантаження, параметри, залежності",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-module-tooling.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-autoload-evolution.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "tty-and-termios",
            "title": "TTY і послідовний порт: модель termios",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-termios.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-teletype.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-serial-port.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "usb-in-linux",
            "title": "USB у Linux: шина, класи, доступ із простору користувача",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-usbfs-ioctl.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-linux-usb-stack.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-libusb-claim.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "interrupts-bottom-halves",
            "title": "Переривання, softirq і робочі черги",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-deferred-work.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-bottom-half.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-threaded-irq-driver.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "dma-and-buffers",
            "title": "DMA і відображення буферів у ядрі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-dma-mapping.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-virt-to-bus.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-ring-and-transfer.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "ioctl-interface",
            "title": "Керуючий канал до драйвера: ioctl",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-ioctl-encoding.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-stty-to-ioctl.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-char-driver-ioctl.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "device-mapper",
            "title": "Device mapper: блоковий пристрій, зібраний із шарів",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-dm-table.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-policy-out-of-kernel.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-live-table-swap.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "dma-buf",
            "title": "dma-buf: спільний буфер між драйверами",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-dmabuf-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-dmabuf-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-dmabuf-share.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "v4l2-video-devices",
            "title": "V4L2: модель відеопристрою в ядрі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-v4l2-ioctls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-v4l-to-v4l2.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-capture-loop.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "block-device-model",
            "title": "Блоковий пристрій: сектори, блоки й черга запитів",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-queue-attributes.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-elevator-to-blkmq.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-watch-merges.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "random-devices",
            "title": "Джерело випадковості в ядрі: /dev/random, /dev/urandom і getrandom",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-random-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-two-devices.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-getting-random-bytes.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "rcu-mechanism",
            "title": "RCU: читання без замків і відкладене звільнення",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-rcu-primitives.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-rcu-lineage.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-rcu-list-module.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "inter-processor-interrupts",
            "title": "Міжпроцесорні переривання: як одне ядро змушує інші виконати код",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-smp-call.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-ipi-latency.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "discard-and-trim",
            "title": "Discard і TRIM: як файлова система каже носієві, що блоки більше не потрібні",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-discard-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-trim-birth.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "cpuidle-and-cstates",
            "title": "Простій ядра процесора: cpuidle і глибина сну",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-cpuidle-sysfs.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-hlt-to-cpuidle.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-break-even.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "lvm-and-snapshots",
            "title": "LVM: логічні томи й миттєві знімки",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-lvm-commands.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-hpux-to-lvm2.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-snapshot-sizing.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "loop-device",
            "title": "Loop-пристрій: файл у вигляді блокового пристрою",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-losetup-and-ioctls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-loop-origins.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-loop-attach.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "dm-verity",
            "title": "dm-verity: блоковий пристрій під деревом Меркла",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-verity-table.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-chromeos-to-android.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-verity-by-hand.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "pseudo-terminal",
            "title": "Псевдотермінал: термінал без заліза",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-pty-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-teletype-to-ptmx.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-pty-driver.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "dm-crypt",
            "title": "dm-crypt: прозоре шифрування блокового пристрою",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-crypt-target.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-cryptoloop-to-luks.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-crypt-by-hand.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "device-tree",
            "title": "Дерево пристроїв: як прошивка описує недискаверабельне залізо",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-dt-bindings.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-board-files.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-i2c-sensor-overlay.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "terminal-escape-sequences",
            "title": "Керуючі послідовності термінала: як програма малює на екрані",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-common-sequences.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-ansi-standard.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-input-parser.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "usb-host-controller",
            "title": "Драйвер контролера хоста USB: xHCI і планування передач",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-xhci-structures.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-framelist-to-rings.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-periodic-bandwidth.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "usb-gadget",
            "title": "USB-gadget: Linux у ролі пристрою, а не хоста",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-configfs-gadget.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-gadget-lineage.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-ffs-function.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "dm-multipath",
            "title": "Multipath: кілька шляхів до одного сховища",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-multipath-table.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-md-multipath-to-dm.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-multipath-on-loop.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "drm-kms",
            "title": "DRM і KMS: модель графічного пристрою в ядрі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-kms-objects.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-ums-to-kms.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-atomic-modeset.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "dma-fence-sync",
            "title": "dma-fence і sync_file: хто каже, що буфер готовий",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-fence-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-fencing-lineage.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-sw-sync.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "media-controller-graph",
            "title": "Media Controller: граф пристроїв замість одного вузла",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-media-ioctls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-graph-api-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-walk-the-graph.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "io-schedulers",
            "title": "Планувальники блокового введення-виведення: none, mq-deadline, BFQ і Kyber",
            "basic": {
              "status": "done",
            "api": [
              {
                "file": "api-scheduler-tunables.md",
                "status": "done",
            "math": [
              {
                "file": "math-fair-queueing.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-measure-schedulers.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-scheduler-tunables.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-measure-schedulers.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-fair-queueing.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "disk-partitions",
            "title": "Розділи диска: таблиця розділів, вирівнювання й що з цього бачить ядро",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-gpt-layout.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-mbr-to-gpt.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-parse-gpt.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "virtio-rng",
            "title": "virtio-rng: непередбачність від гіпервізора до гостьового ядра",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-virtio-rng-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-virtio-rng-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-minimal-rng-driver.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "dm-thin-provisioning",
            "title": "Тонке виділення: dm-thin, спільний пул і повернення місця",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-thin-pool-table.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-arrays-to-dm-thin.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-thin-by-hand.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "secure-erase-and-sanitize",
            "title": "Надійне стирання носія: ATA Secure Erase, Sanitize і чому discard для цього не годиться",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-erase-commands.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-erasure-myths.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-drive-the-sanitize.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "userspace-block-devices",
            "title": "Блоковий пристрій із простору користувача: NBD і ublk",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-ublk-protocol.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-userspace-block-drivers.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-ublk-server.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "dm-integrity",
            "title": "dm-integrity: контрольні суми на записуваному блоковому пристрої",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-integrity-table.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-two-attempts.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-integrity-by-hand.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "runtime-power-management",
            "title": "Присипляння пристрою на ходу: runtime PM",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-runtime-pm.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-usb-to-runtime-pm.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-runtime-pm-driver.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-crypto-api",
            "title": "Криптографічна підсистема ядра: імена алгоритмів і трансформації",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-crypto-transforms.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-two-crypto-apis.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-tfm-in-module.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "platform-bus",
            "title": "Шина platform: дім для заліза, яке не можна перелічити",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-platform-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-pseudo-bus-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-platform-driver.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "terminfo-database",
            "title": "База terminfo: як програма дізнається мову свого термінала",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-terminfo-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-termcap-to-terminfo.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-tparm-interpreter.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "virtual-console",
            "title": "Віртуальна консоль Linux: емулятор термінала всередині ядра",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-console-ioctls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-why-emulator-in-kernel.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-vt-handover.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "usb-bulk-streams",
            "title": "Bulk-стрими USB 3: кілька кілець на одну кінцеву точку",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-stream-contexts.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-streams-and-uasp.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-streams-driver.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "scsi-subsystem",
            "title": "Підсистема SCSI: команди, сенс-коди й обробка помилок",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sense-and-status.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-sasi-to-scsi.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-decode-sense.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "nvme-in-linux",
            "title": "NVMe в Linux: черги, простори імен і власна багатошляховість",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-nvme-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-driver-and-multipath.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-identify-by-ioctl.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "gpu-command-submission",
            "title": "Подання роботи на графічний процесор: черги команд і планувальник",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-submit-ioctls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-relocations-to-softpin.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-sched-driver.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "media-request-api",
            "title": "Медіазапити: параметри й буфер, застосовані до кадру атомарно",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-request-ioctls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-request-lineage.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-per-frame-controls.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "writeback-throttling",
            "title": "Гальмування фонового запису: wbt і цільова затримка читання",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-wbt-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-codel-in-block-layer.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "io-cgroup-control",
            "title": "Обмеження блокового вводу-виводу по cgroup: io.max, io.latency і iocost",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-io-controller-files.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-blkio-to-iocost.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-two-groups-lab.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "zoned-block-devices",
            "title": "Зонований блоковий пристрій: зони, послідовний запис і хто стежить за порядком",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-zone-interface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-shingles-and-honesty.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-walk-the-zones.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "md-raid",
            "title": "Програмний RAID у Linux: md, рівні масиву й відновлення",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-md-metadata.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-md-lineage.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-md-lab.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "virtio-transport",
            "title": "virtio: паравіртуалізована шина й віртчерги",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-virtio-transports.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-virtio-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-ring-walk.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "vm-generation-id",
            "title": "VM Generation ID: як гість дізнається, що його клонували",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-vmgenid-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-vmgenid-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-catch-the-fork.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "sed-opal-drives",
            "title": "Самошифрувальний носій: TCG Opal і підтримка sed-opal у ядрі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-opal-ioctls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-opal-lineage.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-opal-discovery.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "scsi-generic-passthrough",
            "title": "Наскрізні команди до пристрою: SG_IO, ATA passthrough і чому вони йдуть повз блоковий шар",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sg-io-hdr.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-three-doors.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-ask-the-drive.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "block-integrity-profile",
            "title": "Профіль цілісності блокового шару: T10 DIF/DIX і додаткові байти на сектор",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-integrity-interfaces.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-end-to-end-argument.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-pi-by-hand.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "power-domains-genpd",
            "title": "Домени живлення в ядрі: genpd і спільний вимикач на групу пристроїв",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-genpd-provider.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-genpd-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-genpd-provider.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "module-signing",
            "title": "Підпис модулів ядра: чому ядро відмовляється вантажити чужий код",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-signature-trailer.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-module-signing-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-verify-ko-signature.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "driver-probe-and-binding",
            "title": "Прив'язка драйвера до пристрою: probe, збіг за таблицею й відкладена спроба",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-binding-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-ordering-problem.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-probe-driver.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "hwmon",
            "title": "hwmon: клас датчиків у ядрі й одиниці в sysfs",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-hwmon-attributes.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-lm-sensors-to-hwmon.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-hwmon-driver.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "scsi-target-lio",
            "title": "Ціль SCSI в ядрі (LIO): як машина віддає своє сховище",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-configfs-target.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-target-in-mainline.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-target-by-hand.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "input-evdev",
            "title": "Підсистема вводу й evdev: як натиск клавіші стає структурою input_event",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-evdev-interface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-input-core-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-uinput-device.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "persistent-memory-devices",
            "title": "Постійна пам'ять як пристрій: NVDIMM, простори імен і /dev/pmem",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-nd-tree-and-ndctl.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-nvdimm-standardisation.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-survive-a-bad-cell.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "mmio-and-ioremap",
            "title": "Регістри пристрою в пам'яті: ioremap і доступ через readl/writel",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-io-accessors.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-memory-or-ports.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-mmio-driver.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "devres-managed-resources",
            "title": "Керовані ресурси драйвера: сімейство devm_ і автоматичне звільнення",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-devm-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-devres-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-managed-resource.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "ncurses",
            "title": "ncurses: бібліотека повноекранних програм у терміналі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-ncurses-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-curses-to-ncurses.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-minimal-updater.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "fbdev-interface",
            "title": "Кадровий буфер як пристрій: /dev/fb0 і його емуляція поверх DRM",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-fbdev-structs.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-fbdev-to-drm.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-raw-fb-draw.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "usb-mass-storage",
            "title": "Накопичувачі по USB: клас mass storage, драйвери usb-storage і uas",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-bot-vs-uas.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-usb-storage-evolution.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-usb-storage-quirks.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "libata",
            "title": "libata: як ATA-диск потрапляє під SCSI-шар Linux",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sat-translation.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-ide-to-libata.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-libata-sysfs.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "nvme-over-fabrics",
            "title": "NVMe поверх мереж: той самий набір команд по TCP, RDMA і Fibre Channel",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-nvmeof-transports.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-iscsi-to-nvmeof.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-nvmet-setup.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "dm-zoned",
            "title": "dm-zoned: зонований носій під виглядом звичайного",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-zbc-zns-spec.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-dmzoned-setup.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-zone-reclaim-cost.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "vhost-and-vdpa",
            "title": "vhost і vDPA: хто насправді обслуговує віртчергу",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-virtqueue-ring.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-qemu-to-vdpa.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-vdpa-setup.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "clock-framework",
            "title": "Каркас тактування: хто роздає, ділить і вимикає такти пристроїв",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-ccf-functions.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-clk-driver-example.md",
                  "status": "done"
                }
              ],
              "math": [
                {
                  "file": "math-pll-divider-calc.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "regulator-framework",
            "title": "Підсистема регуляторів: хто вмикає напругу для пристрою",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-regulator-functions.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-regulator-driver.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "pm-qos-constraints",
            "title": "PM QoS: обмеження затримки як контракт від споживача до ядра",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "device-links",
            "title": "Зв'язки між пристроями: явне ребро «постачальник — споживач» поверх дерева",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-device-link-flags.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-device-link-example.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "dkms-out-of-tree-modules",
            "title": "DKMS: перезбирання й підписування позадеревних модулів під кожне ядро",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "thermal-framework",
            "title": "Тепловий каркас ядра: зони, точки спрацювання й пристрої охолодження",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-thermal-sysfs.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-thermal-governor.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "iscsi-in-linux",
            "title": "iSCSI: SCSI поверх TCP — сесії, IQN і портали",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-iscsi-pdu.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-iscsi-standard.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-iscsi-target-setup.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "scsi-persistent-reservations",
            "title": "Постійні резервації SCSI: як вузли кластера ділять один диск",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-scsi-pr-commands.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-cluster-fencing-pr.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "hid-subsystem",
            "title": "Підсистема HID: дескриптор звітів і як пристрій сам описує свої органи керування",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-hid-report-items.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-hid-standard.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-hidraw-reader.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "multitouch-protocol",
            "title": "Протокол мультидотику: слоти, контакти й два способи їх описати",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "magic-sysrq",
            "title": "Магічний SysRq: аварійні команди ядра з клавіатури",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "opp-tables",
            "title": "Таблиці робочих точок (OPP): частота, напруга й рівень домену",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-opp-functions.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-opp-dt-example.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "machine-check-and-ras",
            "title": "Апаратні помилки: машинна перевірка (MCE) і як ядро про них дізнається",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "cxl-memory-devices",
            "title": "Пам'ять на CXL: пристрої третього типу й області",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-cxl-spec.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-cxl-cli.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "pci-in-linux",
            "title": "PCI у Linux: конфігураційний простір, вікна BAR і перелічення пристроїв",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-pci-config-space.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "vfio-passthrough",
            "title": "Парапрохідність пристроїв та IOMMU-групи (VFIO)",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-vfio-ioctl.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-kvm-assign-to-vfio.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-userspace-pci-driver.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "sr-iov-virtual-functions",
            "title": "Апаратне розділення пристроїв (SR-IOV)",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-sriov-pci-cap.md",
                "status": "done",
            "comp": [
              {
                "file": "comp-eswitch-architecture.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-sriov-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-sriov-manager.md",
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
              "status": "done"
            }
          },
          {
            "slug": "virtio-pci-spec",
            "title": "Специфікація Virtio: virtqueues та vring",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-virtio-pci-caps.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-virtio-oasis-standard.md",
                "status": "done",
            "math": [
              {
                "file": "math-vring-indexing.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-vring-user-driver.md",
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
              "status": "done"
            }
          },
          {
            "slug": "xen-dom0-domu",
            "title": "Гіпервізор Xen: Dom0, DomU та grant tables",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-xenstore-gnttab.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-xen-paravirtualization.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-grant-table-io.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "nvme-over-fabrics-rdma-tcp",
            "title": "NVMe over Fabrics (NVMe-oF)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "pcie-express-bus-subsystem",
            "title": "Підсистема PCI Express",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "usb-core-subsystem",
            "title": "Ядро підсистеми USB",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-usb-core-functions.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-usb-core-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-urb-async-engine.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "cpufreq-and-cpuidle",
            "title": "Управління частотою та станами CPU (cpufreq, cpuidle)",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-cpufreq-cpuidle-sysfs.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-dvfs-and-acpi-origin.md",
                "status": "done",
            "math": [
              {
                "file": "math-dvfs-power-and-residency.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-cpufreq-governor-and-qos.md",
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
              "status": "done"
            }
          },
          {
            "slug": "thermal-management-framework",
            "title": "Термальний фреймворк ядра",
            "basic": {
              "status": "empty",
            "api": [
              {
                "file": "api-sysfs-and-netlink.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-thermal-evolution.md",
                "status": "done",
            "math": [
              {
                "file": "math-power-allocator-pid.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-thermal-monitor.md",
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
              "status": "done"
            }
          },
          {
            "slug": "vdpa-virtio-data-path-acceleration",
            "title": "Апаратне прискорення Virtio: vDPA та SmartNIC",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-vdpa-kernel-ops.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-vdpa-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-vdpa-ioctl-query.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            }
          },
          {
            "slug": "nested-virtualization-kvm",
            "title": "Вкладена віртуалізація у KVM (Nested VT-x/AMD-V)",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-kvm-nested-sysfs-and-msr.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-shadow-vmcs-and-nested-evolution.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-kvm-nested-control-and-ioctl.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            }
          },
          {
            "slug": "confidential-computing-sev-tdx",
            "title": "Конфіденційні обчислення: AMD SEV-SNP та Intel TDX",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-guest-attestation.md",
                "status": "done",
            "comp": [
              {
                "file": "comp-memory-encryption-engines.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-confidential-computing.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-guest-report-fetch.md",
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
          },
          {
            "slug": "cxl-compute-express-link",
            "title": "Шина CXL (Compute Express Link) та пулінг пам’яті",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-sysfs-cxl.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-cxl-origin.md",
                "status": "done",
            "math": [
              {
                "file": "math-cxl-interleave-mapping.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-cxl-numa-alloc.md",
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
          },
          {
            "slug": "viommu-virtual-iommu",
            "title": "Віртуальний IOMMU (vIOMMU) для вкладеного прокидання",
            "detailed": {
              "status": "update"
            },
            "basic": {
              "status": "done"
            }
          },
          {
            "slug": "virtio-fs-and-virtio-gpu",
            "title": "Спеціалізовані пристрої Virtio: virtio-fs та virtio-gpu",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "nvme-zoned-namespaces-zns",
            "title": "Зонований простір імен NVMe (ZNS)",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "i3c-bus-subsystem",
            "title": "Підсистема шини I3C (MIPI I3C)",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-i3c-subsystem.md",
                "status": "done",
            "comp": [
              {
                "file": "comp-i3c-master-controller.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-mipi-i3c.md",
                "status": "done",
            "math": [
              {
                "file": "math-i3c-arbitration.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-i3c-driver.md",
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
          },
          {
            "slug": "pci-peer-to-peer-p2pdma",
            "title": "Прямий доступ між пристроями PCIe (P2PDMA)",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-p2pdma-kernel.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-p2p-dma-evolution.md",
                "status": "done",
            "math": [
              {
                "file": "math-p2p-throughput-latency.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-p2pdma-driver.md",
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
          },
          {
            "slug": "drm-kms-display-pipeline",
            "title": "Прямий рендеринг ядра DRM/KMS: атомне перемикання режимів",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-drm-kms-properties.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-x11-to-atomic-kms.md",
                "status": "done",
            "math": [
              {
                "file": "math-display-bandwidth-calc.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-atomic-kms-flip.md",
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
          },
          {
            "slug": "spdm-device-attestation",
            "title": "Протокол атестації пристроїв SPDM на шинах PCIe",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-spdm-kernel-sysfs.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-spdm-genesis.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-spdm-attestation-verifier.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            }
          },
          {
            "slug": "sound-open-firmware-sof",
            "title": "Аудіоплатформа Sound Open Firmware (SOF) та ALSA SoC",
            "detailed": {
              "status": "done",
            "api": [
              {
                "file": "api-ipc.md",
                "status": "done",
            "hist": [
              {
                "file": "hist-sof.md",
                "status": "done",
            "proj": [
              {
                "file": "proj-pcm-stream.md",
                "status": "done"
              }
            ],
              }
            ],
              }
            ],
            }
          },
          {
            "slug": "v4l2-media-controller-api",
            "title": "Відео-підсистема V4L2 та Media Controller API",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "input-evdev-subsystem",
            "title": "Підсистема введення evdev та події /dev/input/eventX",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "gpio-gpiod-descriptor-api",
            "title": "Сучасний двоврівневий API GPIO descriptors (gpiod)",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "counter-subsystem-quadrature",
            "title": "Підсистема лічильників ядра Counter subsystem (Hardware Quadrature Encoders)",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "iio-industrial-io-subsystem",
            "title": "Підсистема Industrial I/O (IIO) для аналогових сенсорів та ADC/DAC",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "wmi-windows-management-instrumentation",
            "title": "Інтерфейс WMI (ACPI-WMI) у драйверах Linux",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "hwrng-hardware-random-number-generator",
            "title": "Підсистема апаратних генераторів випадкових чисел (hwrng) та entropy pool",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "drm-accel-compute-subsystem",
            "title": "Підсистема прискорювачів DRM Accel (/dev/accel/accelX для NPU та AI-чіпів)",
            "detailed": {
              "status": "update"
            }
          }
        ]
      },
      {
        "slug": "boot-init",
        "title": "Завантаження й служби",
        "scope": "Шлях від увімкнення живлення до працюючої системи та як тримають служби.",
        "topics": [
          { slug: "tmpfiles-d-runtime-volatile-files", title: "Управління тимчасовими файлами: сервіс systemd-tmpfiles та tmpfiles.d", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-tmpfiles-spec.md", status: "done" }] , "hist": [{ file: "hist-volatile-storage-evolution.md", status: "done" }] , "proj": [{ file: "proj-custom-tmpfiles-service.md", status: "done" }] },
          { slug: "systemd-sysusers-and-sysctl-d", title: "Декларативне налаштування системи: systemd-sysusers та systemd-sysctl", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-sysusers-and-sysctl-formats.md", status: "done" }] , "comp": [{ file: "comp-dot-d-hierarchy-precedence.md", status: "done" }] , "hist": [{ file: "hist-declarative-sysconfig-evolution.md", status: "done" }] , "proj": [{ file: "proj-declarative-provisioning-engine.md", status: "done" }] },
          { slug: "systemd-nspawn-lightweight-containers", title: "Контейнеризація у systemd: інструмент systemd-nspawn", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-nspawn-cli-and-nspawn-file.md", status: "done" }] , "hist": [{ file: "hist-chroot-to-nspawn.md", status: "done" }] , "proj": [{ file: "proj-nspawn-custom-container.md", status: "done" }] },
          { slug: "systemd-generator-architecture", title: "Генератори systemd (/lib/systemd/system-generators/)", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-generator-interface.md", status: "done" }] , "hist": [{ file: "hist-generators-evolution.md", status: "done" }] , "proj": [{ file: "proj-custom-generator.md", status: "done" }] },
          { slug: "systemd-target-units-and-boot-targets", title: "Цільові юніти (target) та ізоляція рівнів виконання systemd", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-target-unit-spec.md", status: "done" }] , "hist": [{ file: "hist-runlevels-to-targets.md", status: "done" }] , "proj": [{ file: "proj-custom-target-and-isolation.md", status: "done" }] },
          { slug: "systemd-boot-and-systemd-stub-uki", title: "Завантажувачі UEFI: systemd-boot та Unified Kernel Images (UKI)", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-uki-sections.md", status: "done" }] , "hist": [{ file: "hist-uki-evolution.md", status: "done" }] , "proj": [{ file: "proj-build-uki.md", status: "done" }] },
          { slug: "journald-logging-subsystem-and-journalctl", title: "Логування у systemd: підсистема journald та інструмент journalctl", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-sd-journal.md", status: "done" }] , "hist": [{ file: "hist-syslog-to-journald.md", status: "done" }] , "math": [{ file: "math-journal-fss-sealing.md", status: "done" }] , "proj": [{ file: "proj-journalctl-emulator.md", status: "done" }] },
          { slug: "dracut-and-mkinitcpio-toolchains", title: "Генератори initramfs: dracut, mkinitcpio та initramfs-tools", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-toolchain-hook-interfaces.md", status: "done" }] , "hist": [{ file: "hist-initramfs-generators-evolution.md", status: "done" }] , "proj": [{ file: "proj-custom-dracut-module.md", status: "done" }] },
          { slug: "systemd-systemctl-and-unit-files", title: "Системний менеджер systemd: unit-файли та systemctl", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-systemctl-dbus.md", status: "done" }] , "hist": [{ file: "hist-systemctl-evolution.md", status: "done" }] , "proj": [{ file: "proj-dbus-unit-control.md", status: "done" }] },
          { slug: "initramfs-and-initrd-architecture", title: "Архітектура initramfs та cpio: розгортання раннього простору користувача", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-cpio-header-spec.md", status: "done" }] , "comp": [{ file: "comp-initrd-initramfs-memory.md", status: "done" }] , "hist": [{ file: "hist-ramdisk-to-rootfs.md", status: "done" }] , "proj": [{ file: "proj-cpio-unpack-engine.md", status: "done" }] },
          { slug: "kernel-boot-process-from-reset-vector-to-start-kernel", title: "Завантаження ядра: від вектора скидання процесора до start_kernel", basic: { status: "empty" }, detailed: { status: "done" } , "api": [{ file: "api-boot-params-header.md", status: "done" }] , "hist": [{ file: "hist-real-mode-legacy-boot.md", status: "done" }] , "math": [{ file: "math-early-paging-layout.md", status: "done" }] , "proj": [{ file: "proj-parse-vmlinuz-header.md", status: "done" }] },
          {
            "slug": "boot-chain",
            "title": "Ланцюг завантаження: від прошивки до init",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-chain-shape.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-walk-the-chain.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "bootloader-and-cmdline",
            "title": "Завантажувач і командний рядок ядра",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-cmdline-reference.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-multiboot-and-grub.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-uki-by-hand.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "initramfs",
            "title": "initramfs: тимчасовий корінь",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-initrd-to-initramfs.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-tiny-initramfs.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "init-and-pid1",
            "title": "Роль init і особливість PID 1",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "hist": [
                {
                  "file": "hist-shapes-of-init.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-minimal-init.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "systemd-model",
            "title": "systemd: юніти, залежності, цілі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-unit-directives.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-runlevels-to-units.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-see-the-transaction.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "service-lifecycle",
            "title": "Життєвий цикл служби й політика перезапуску",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-service-unit.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-supervision.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-notify-watchdog.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "socket-activation",
            "title": "Активація за сокетом",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-listen-fds.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-inetd.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-activated-service.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "journald-logging",
            "title": "journald: журнал як структуровані записи",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-journal-protocol.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-syslog-birth.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-journal-reader.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "suspend-and-resume",
            "title": "Призупинення й пробудження: suspend, hibernate і стан пристроїв",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-sleep-controls.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-swsusp.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-suspend-aware-program.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kernel-initcalls",
            "title": "Ініціалізація підсистем ядра: initcall і порядок стартів",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-initcall-reference.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-initcall-levels.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-initcall-lab.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "logind-sessions-seats",
            "title": "systemd-logind: сеанси, місця (seats) і хто зараз за комп'ютером",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-login1-dbus.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-from-utmp-to-logind.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-session-device-handover.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "dynamic-service-users",
            "title": "DynamicUser: обліковий запис, що живе рівно стільки, скільки служба",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-dynamic-user-surface.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-service-accounts.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-uid-lock-by-hand.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "uefi-firmware",
            "title": "UEFI: прошивка як середовище виконання",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-efi-variables.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-efi-to-uefi.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-hello-uefi.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "secure-boot",
            "title": "Secure Boot: перевірений ланцюг завантаження",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-secure-boot-variables.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-shim-and-mok.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-own-keys.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "orderly-shutdown",
            "title": "Впорядковане вимкнення: як система зупиняється",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-reboot-syscall.md",
                  "status": "done"
                }
              ],
              "hist": [
                {
                  "file": "hist-sysvinit-to-systemd-shutdown.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-shutdown-inhibitor.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "service-sandboxing",
            "title": "Пісочниця служби: ProtectSystem, PrivateTmp і решта обмежень юніта",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "service-directories",
            "title": "Керовані каталоги служби: RuntimeDirectory, StateDirectory і хто їх прибирає",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done",
              "api": [
                {
                  "file": "api-service-directories.md",
                  "status": "done"
                }
              ],
              "proj": [
                {
                  "file": "proj-dynamic-user-dirs.md",
                  "status": "done"
                }
              ]
            }
          },
          {
            "slug": "kexec-and-kdump",
            "title": "kexec: завантаження нового ядра без прошивки, і kdump",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "firmware-capsule-updates",
            "title": "Оновлення прошивки з-під системи: капсули UEFI, таблиця ESRT і fwupd",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "measured-boot-pcr",
            "title": "Виміряне завантаження: регістри PCR і журнал подій",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "service-notify-protocol",
            "title": "Протокол сповіщення менеджера: NOTIFY_SOCKET, READY=1 і Type=notify",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "sysusers-declarative-accounts",
            "title": "systemd-sysusers: облікові записи, описані декларативно",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "init-sections",
            "title": "Секції ініціалізації: код і дані, які ядро викидає після завантаження",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "acpi-tables-and-namespace",
            "title": "ACPI: таблиці прошивки й простір імен, з якого ядро дізнається про залізо",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "device-tree-flattened-dtb",
            "title": "Дерево пристроїв (Device Tree, DTB)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          }
        ]
      },
      {
        "slug": "shell",
        "title": "Оболонка як модель",
        "scope": "Оболонка не як набір команд, а як механізм складання процесів і потоків даних.",
        "topics": [
          {
            "slug": "shell-role",
            "title": "Оболонка: що вона робить насправді",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "argv-and-environment",
            "title": "argv, оточення й що успадковує дитина",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "standard-streams",
            "title": "Три потоки: stdin, stdout, stderr",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "redirection-model",
            "title": "Перенаправлення як робота з дескрипторами",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "pipeline-composition",
            "title": "Конвеєр: композиція процесів",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "exit-status",
            "title": "Код виходу як інтерфейс програми",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "expansion-and-quoting",
            "title": "Розкриття й лапки: коли текст стає аргументами",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "job-control",
            "title": "Керування завданнями: PGID, управляючий термінал, SIGTSTP і сигнальні групи",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "session-environment",
            "title": "Оточення сеансу: profile, rc і пошук у PATH",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "locale-and-collation",
            "title": "Локаль: як мова змінює поведінку програм",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          }
        ]
      },
      {
        "slug": "networking",
        "title": "Мережа в ядрі",
        "scope": "Як Linux бачить мережу зсередини: від інтерфейсу до маршруту й фільтра.",
        "topics": [
          { slug: "network-stack-architecture", title: "Мережевий стек ядра Linux: архітектура та шлях пакета", basic: { status: "done" }, detailed: { status: "done" } },
          { slug: "netfilter-and-iptables-nftables", title: "Netfilter, iptables та nftables", basic: { status: "done" }, detailed: { status: "done" } },
          {
            "slug": "network-stack",
            "title": "Мережевий стек у ядрі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "interfaces-and-addresses",
            "title": "Інтерфейси, адреси й стан лінка",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "socket-api-linux",
            "title": "Сокети в Linux: від дескриптора до з'єднання",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "routing-decision",
            "title": "Таблиця маршрутів і рішення про маршрут",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "netfilter-model",
            "title": "netfilter: ланцюги, таблиці й NAT",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "network-namespaces",
            "title": "Мережеві простори імен, veth і мости",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "name-resolution-path",
            "title": "Шлях розв'язання імені: NSS, resolv, systemd-resolved",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "tun-tap",
            "title": "TUN/TAP: віртуальні інтерфейси",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "netlink-protocol",
            "title": "Обмін повідомленнями через netlink",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "nic-offloads",
            "title": "Розвантаження мережевої карти: контрольні суми, збирання й сегментація",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "kernel-tls",
            "title": "TLS усередині ядра: шар записів на сокеті",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "out-of-band-data",
            "title": "Термінові дані TCP: покажчик терміновости, MSG_OOB і SIGURG",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "ipsec-xfrm",
            "title": "IPsec у Linux: каркас перетворень xfrm",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "rdma-in-linux",
            "title": "RDMA: віддалений прямий доступ до пам'яті",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "tcp-connection-liveness",
            "title": "Виявлення мертвого TCP-з'єднання: keepalive, TCP_USER_TIMEOUT і прикладна перевірка",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "vhost-net-acceleration",
            "title": "Прискорення мережі у віртуалізації (vhost-net)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "xdp-express-data-path",
            "title": "eXpress Data Path (XDP): обробка пакетів на NIC",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "wireguard-kernel-architecture",
            "title": "Ядерний тунель WireGuard",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "ebpf-traffic-control-clsact",
            "title": "eBPF у підсистемі Traffic Control",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "bonding-and-team-drivers",
            "title": "Агрегація каналів: Bonding та Team",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "macvlan-macvtap-drivers",
            "title": "Драйвери Macvlan та Macvtap",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "multipath-tcp-mptcp",
            "title": "Багатошляховий TCP (MPTCP)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "xdp-sockets-af-xdp",
            "title": "Сокети високої швидкості AF_XDP (XSK)",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "io-uring-net-passthrough",
            "title": "Мережевий ввід-вивід io_uring: SendZC та RecvZC",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "bpf-sockmap-and-sk-skb",
            "title": "Прискорення сокетів BPF: sockmap та sk_skb",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "ethtool-netlink-interface",
            "title": "Сучасний інтерфейс налаштування мережі ethtool Netlink",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "packet-mmap-ring-buffers",
            "title": "Механізм PACKET_MMAP (TPACKET_V3 ring buffers)",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "mptcp-path-managers",
            "title": "Менеджери шляхів у MPTCP (mptcpd та in-kernel path manager)",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "netfilter-nftables-expression-engine",
            "title": "Рушій виразів nftables у ядрах Linux (nftables vs iptables)",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "bpf-cgroup-skb-hooks",
            "title": "Хуки eBPF на рівні cgroup: BPF_CGROUP_INET_INGRESS/EGRESS",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "macsec-ieee-802-1ae",
            "title": "Захист канального рівня MACsec (IEEE 802.1AE) у ядрі",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "netfilter-conntrack-architecture",
            "title": "Підсистема відстеження зʼєднань Conntrack (nf_conntrack) та conntrack tables",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "ethtool-rss-indirection-tables",
            "title": "Масштабування на боці прийому: RSS Indirection Tables та Flow Hashing",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "tls-ktls-kernel-offload",
            "title": "Ядерне прискорення TLS (kTLS / TLS_HW / TLS_SW)",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "xdp-cpumap-and-devmap",
            "title": "Маршрутизація XDP: BPF_MAP_TYPE_CPUMAP та BPF_MAP_TYPE_DEVMAP",
            "detailed": {
              "status": "update"
            }
          }
        ]
      },
      {
        "slug": "linking",
        "title": "Від файлу до процесу",
        "scope": "Що відбувається між «є виконуваний файл» і «є працюючий процес».",
        "topics": [
          {
            "slug": "elf-structure",
            "title": "ELF: сегменти, секції, точка входу",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "static-and-dynamic-linking",
            "title": "Статичне й динамічне лінкування",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "dynamic-loader",
            "title": "Динамічний завантажувач і його робота",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "soname-versioning",
            "title": "SONAME і версіонування спільних бібліотек",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "library-search-order",
            "title": "Порядок пошуку бібліотек: rpath, LD_LIBRARY_PATH, кеш",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "symbol-resolution",
            "title": "Розв'язання символів і перекриття (interposition)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "plt-and-got",
            "title": "PLT і GOT: як працює виклик через межу бібліотеки",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "library-abi-compat",
            "title": "Сумісність ABI бібліотеки й що її ламає",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "vdso",
            "title": "vDSO: бібліотека від ядра в кожному процесі",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "elf-tls",
            "title": "TLS в ELF: як потік дістає власні глобальні змінні",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "auxiliary-vector",
            "title": "Допоміжний вектор ELF: що ядро передає програмі на старті",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "position-independent-code",
            "title": "Позиційно-незалежний код: PIC, PIE й ціна непрямості",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          }
        ]
      },
      {
        "slug": "observability",
        "title": "Побачити, що відбувається",
        "scope": "Механізми, якими система показує себе зсередини — і що з них можна дізнатися.",
        "topics": [
          { slug: "systemtap-scripting", title: "Інструментарій SystemTap", basic: { status: "empty" }, detailed: { status: "done" } },
          { slug: "bpftrace-dynamic-tracing", title: "Високорівневе трасування через bpftrace", basic: { status: "empty" }, detailed: { status: "done" } },
          { slug: "audit-framework", title: "Підсистема аудиту ядра: правила, події й auditd", basic: { status: "done" }, detailed: { status: "done" } },
          {
            "slug": "proc-filesystem",
            "title": "/proc: процеси як файли",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "ptrace-model",
            "title": "ptrace: на чому тримається трасування й налагодження",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "syscall-tracing",
            "title": "Трасування системних викликів",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "perf-events",
            "title": "Підсистема perf: лічильники й вибірковий профіль",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "ftrace-kernel-tracing",
            "title": "Трасування ядра ftrace (/sys/kernel/tracing, function, tracepoints, trace-cmd)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "ebpf-extended-berkeley-packet-filter",
            "title": "eBPF (Extended Berkeley Packet Filter): власні програми всередині ядра",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "core-dump",
            "title": "Аварійний дамп: як налаштувати й що з нього видно",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "load-and-pressure",
            "title": "Середнє навантаження й тиск на ресурси (PSI)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "kernel-oops-panic",
            "title": "Oops і паніка: що система робить, коли падає саме ядро",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "uprobes-and-kprobes",
            "title": "Динамічне трасування: kprobes та uprobes",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "audit-subsystem",
            "title": "Підсистема аудиту ядра: правила, події й auditd",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "done"
            }
          },
          {
            "slug": "kernel-log-printk",
            "title": "Журнал ядра: printk, рівні важливості й dmesg",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "latency-tracers",
            "title": "Трасувальники затримок: osnoise, timerlat і rtla",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "syslog-protocol",
            "title": "Syslog: пріоритет, засоби (facility) і формат повідомлення",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "kallsyms-and-system-map",
            "title": "kallsyms: імена символів усередині ядра, System.map і %pS",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "debugfs",
            "title": "debugfs: службове вікно в нутрощі ядра",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "systemtap-and-bpftrace",
            "title": "Високорівневе трасування: SystemTap та bpftrace",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "lockdep-lock-validator",
            "title": "Валідатор блокувань Lockdep",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "kasan-kernel-address-sanitizer",
            "title": "Kernel Address Sanitizer (KASAN)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "kcsan-concurrency-sanitizer",
            "title": "Kernel Concurrency Sanitizer (KCSAN)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "kmemleak-leak-detector",
            "title": "Виявлення витоків пам'яті ядра (Kmemleak)",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "bpf-iterators-and-user-ringbuf",
            "title": "Ітератори BPF (bpf_iter) та User Ring Buffer",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "bpf-trampoline-and-fprobe",
            "title": "Сучасні оверхеди трасування: BPF Trampoline та fprobe",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "ebpf-perf-event-array",
            "title": "Канали подій eBPF Perf Event Array",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "user-events-ftrace-subsystem",
            "title": "Користувацькі події у ftrace: User Events підсистема",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "ebpf-arena-shared-memory-region",
            "title": "Спільні регіони памʼяті BPF Arena (Linux 6.8+)",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "kernel-kunit-test-framework",
            "title": "Фреймворк тестування ядра KUnit та відлагоджувачі KASAN/KCSAN/KFENCE",
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "bpf-ringbuf-vs-perfbuf",
            "title": "Порівняльний аналіз механізмів доставки подій BPF Ring Buffer vs Perf Event Array",
            "detailed": {
              "status": "update"
            }
          }
        ]
      },
      {
        "slug": "packaging",
        "title": "Постачання програм",
        "scope": "Як програма доходить до користувача і чому способів кілька.",
        "topics": [
          {
            "slug": "package-manager-model",
            "title": "Модель пакетного менеджера",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "deb-and-rpm",
            "title": "deb і rpm: два світи пакування",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "repositories-and-trust",
            "title": "Репозиторії, підписи й довіра",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "dependency-resolution",
            "title": "Розв'язання залежностей і конфлікти версій",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "fhs-layout",
            "title": "Ієрархія файлової системи: куди що кладуть",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "self-contained-bundles",
            "title": "Самодостатні пакунки: AppImage, Flatpak, Snap",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "containers-vs-packages",
            "title": "Контейнер проти пакунка",
            "basic": {
              "status": "done"
            },
            "detailed": {
              "status": "update"
            }
          },
          {
            "slug": "multilib-multiarch",
            "title": "Multilib і multiarch: два комплекти бібліотек в одній ієрархії",
            "basic": {
              "status": "empty"
            },
            "detailed": {
              "status": "update"
            }
          }
        ]
      }
    ]
  }
];
