window.__BOOKS__ = window.__BOOKS__ || [];
window.__BOOKS__.push({
  "type": "book",
  "slug": "communications",
  "title": "Зв'язок",
  "sections": [
    {
      "slug": "interfaces",
      "title": "Послідовні інтерфейси",
      "scope": "UART, RS-422/485, струмова петля та стандарти модемів",
      "topics": [
        {
          "slug": "uart",
          "title": "UART: апаратний модуль і периферійний контролер",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-uart-driver.md",
              "status": "done"
            }
          ],
          "comp": [
            {
              "file": "comp-level-shifters.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-16550.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-baud-calculator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "rs422-rs485",
          "title": "RS-422 і RS-485: диференційний послідовний зв'язок",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-spec-comparison.md",
              "status": "done"
            }
          ],
          "comp": [
            {
              "file": "comp-transceivers.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-standardization.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-dir-control.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "modem-standards-v-series",
          "title": "Стандарти модемів серії V (ITU-T)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-v24-v28-signals.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-vseries-evolution.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-v90-pcm-capacity.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-v21-fsk-modem.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "current-loop",
          "title": "Струмова петля: послідовний цифровий та аналоговий інтерфейс",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-optocouplers.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-teletype-to-midi.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-current-loop-uart.md",
              "status": "done"
            }
          ]
        }
      ]
    },
    {
      "slug": "information-theory",
      "title": "Теорія інформації",
      "scope": "Математична межа стиснення й передачі: ентропія, пропускна здатність каналу, теореми Шеннона.",
      "topics": [
        {
          "slug": "bandwidth-capacity",
          "title": "Смуга і межа Шеннона",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-shannon-capacity.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "shannon-entropy",
          "title": "Ентропія Шеннона",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-entropy-name.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-entropy-axioms.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "channel-coding-theorem",
          "title": "Теорема Шеннона про кодування каналу",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-approaching-the-limit.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-random-coding.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-simulate-threshold.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "awgn-channel",
          "title": "Канал AWGN",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-johnson-nyquist.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-gaussian-noise.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-awgn-simulation.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "mutual-information",
          "title": "Взаємна інформація",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-naming.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-mi-identities.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-estimate-mutual-information.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "binary-symmetric-channel",
          "title": "Двійковий симетричний канал",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-capacity-derivation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-bsc-simulation.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "conditional-entropy",
          "title": "Умовна ентропія",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-equivocation.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-chain-rule.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-conditional-entropy.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "erasure-channel",
          "title": "Канал зі стиранням",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "empty"
          },
          "hist": [
            {
              "file": "hist-elias-erasure.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-erasure-recovery.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "binary-erasure-channel",
          "title": "Двійковий канал зі стиранням",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "empty"
          },
          "hist": [
            {
              "file": "hist-elias-erasure.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-capacity-erasure.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "log-likelihood-ratio",
          "title": "Логарифм відношення правдоподібностей (LLR)",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-likelihood-ratio.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-llr-demapper.md",
              "status": "done"
            }
          ]
        }
      ]
    },
    {
      "slug": "coding-theory",
      "title": "Кодування",
      "scope": "Захист повідомлення від помилок і його компактне подання кодами джерела й каналу.",
      "topics": [
        {
          "slug": "parity-bit",
          "title": "Біт парності",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-parity-in-code.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "checksums",
          "title": "Контрольні суми",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-checksum-arithmetic.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-checksums-in-code.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "crc",
          "title": "CRC",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-hardware-crc.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-gf2-polynomials.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-crc-implementation.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "hamming-distance",
          "title": "Відстань Геммінга",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-hamming-1950.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "hamming-code",
          "title": "Код Геммінга",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-hamming-codec.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "ecc-ram-flash",
          "title": "ECC у пам'яті",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-ecc-hardware.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "reed-solomon",
          "title": "Рід–Соломон",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-voyager-codes.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "internet-checksum",
          "title": "Інтернет-контрольна сума (IP/TCP/UDP)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-internet-checksum.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-incremental-update.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-tcp-udp-checksum.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "adler-32",
          "title": "Adler-32",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-adler-zlib.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-adler32-in-code.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "concatenated-codes",
          "title": "Конкатеновані коди",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-forney-concatenation.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-concatenation-params.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-concatenated-pipeline.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "memory-scrubbing",
          "title": "Memory scrubbing: фоновий ремонт пам'яті",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-scrub-race.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-scrub-loop.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "ldpc",
          "title": "LDPC: код розрідженої перевірки паритету",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-gallager.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-belief-propagation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-bit-flipping-decoder.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "flash-wear-leveling",
          "title": "Wear leveling у Flash-пам'яті",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-uber-rber.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-device-uber.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "secded",
          "title": "SECDED: виправити один біт, виявити два",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-hsiao-code.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-secded-distance.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-secded-codec.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "perfect-codes",
          "title": "Досконалі коди",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-golay-codes.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-sphere-packing-bound.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-perfect-code-check.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "linear-block-codes",
          "title": "Лінійні блокові коди",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-slepian-group-codes.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-linear-codec.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "2d-parity",
          "title": "Двовимірна парність",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-tape-vrc-lrc.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-2d-parity.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "burst-error",
          "title": "Пакетна помилка (burst error)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-fire-code.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-reiger-bound.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-burst-simulation.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "convolutional-codes",
          "title": "Згорткові коди",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-elias-viterbi.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-generator-polynomials.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-viterbi-decoder.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "bch-codes",
          "title": "Коди BCH",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-bch-origins.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-bch-bound.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-bch-codec.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "interleaving",
          "title": "Перемішування (interleaving)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-interleaving-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-interleaving-depth.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-interleaver-code.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "linear-codes",
          "title": "Лінійні коди",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-subspace-duality.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "ber-snr-curve",
          "title": "BER і SNR: крива надійності каналу",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-q-function-ber.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-ber-monte-carlo.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "gilbert-elliott-model",
          "title": "Модель Гілберта–Елліота: пакетні помилки",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-gilbert-elliott.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-burst-statistics.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-channel-simulator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "fec-channel-coding",
          "title": "FEC для потокового відео",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-fountain-codes.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-fec-overhead.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-packet-fec.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "ecc-flash",
          "title": "ECC у флеш-пам'яті",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-code-escalation.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-vth-overlap.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-soft-read.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "turbo-codes",
          "title": "Турбокоди",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-turbo-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-iterative-decoding.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-turbo-decoder.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "polar-codes",
          "title": "Полярні коди",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-arikan.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-channel-polarization.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-successive-cancellation.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "golay-code",
          "title": "Коди Голея",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-golay-construction.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-golay-codec.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "reed-muller-code",
          "title": "Коди Ріда–Маллера",
          "basic": {
            "status": "recheck",
          "hist": [
            {
              "file": "hist-mars-mariner.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-plotkin-recursion.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-majority-decoder.md",
              "status": "recheck"
            }
          ],
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-mars-mariner.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-plotkin-recursion.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-majority-decoder.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "cyclic-codes",
          "title": "Циклічні коди",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-prange.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-generator-polynomial.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-cyclic-codec.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "fountain-codes",
          "title": "Фонтанні коди",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-digital-fountain.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-soliton-distribution.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-lt-codec.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "viterbi-algorithm",
          "title": "Алгоритм Вітербі",
          "basic": {
            "status": "recheck",
          "math": [
            {
              "file": "math-branch-metric.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-hmm-viterbi.md",
              "status": "recheck"
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-branch-metric.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-hmm-viterbi.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "viterbi-decoder",
          "title": "Декодер Вітербі",
          "basic": {
            "status": "recheck",
          "math": [
            {
              "file": "math-ml-metric.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-survivor-memory.md",
              "status": "recheck"
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-ml-metric.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-survivor-memory.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "product-codes",
          "title": "Добуткові коди",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "punctured-codes",
          "title": "Виколоті коди (puncturing)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-rcpc-cain-hagenauer.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-punctured-distance.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-punctured-viterbi.md",
              "status": "done"
            }
          ]
        }
      ]
    },
    {
      "slug": "modulation",
      "title": "Модуляція",
      "scope": "Накладання інформації на несучу: амплітудні, частотні, фазові та квадратурні схеми.",
      "topics": [
        {
          "slug": "why-modulation",
          "title": "Навіщо модуляція",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-armstrong.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "am-fm",
          "title": "AM і FM",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-am-fm-synthesis.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "fsk-psk",
          "title": "FSK і PSK",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-iq-plane.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "spread-spectrum",
          "title": "Розширений спектр",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-hedy-lamarr.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "analog-video",
          "title": "Аналогове відео",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "ofdm",
          "title": "OFDM: мультиплексування з ортогональними піднесними",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-ofdm-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-orthogonality-ifft.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-ofdm-modem.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "ssb-modulation",
          "title": "Односмугова модуляція (SSB)",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-ssb-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-phasing-cancellation.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "fm-capture-effect",
          "title": "Ефект захоплення FM",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-armstrong-capture.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-capture-derivation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-capture-simulation.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "cvbs-signal",
          "title": "Композитний відеосигнал CVBS: рівні, тайминг, IRE",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-quadrature-color.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-cvbs-generator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "interlacing",
          "title": "Черезрядкова розгортка (interlacing): поля, зубчастий vsync, twitter",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-ballard-interlace.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-serrated-integrator.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-deinterlacer.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "osd-overlay",
          "title": "OSD-накладання телеметрії на аналоговий відеосигнал",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-max7456-registers.md",
              "status": "done"
            }
          ],
          "comp": [
            {
              "file": "comp-analog-keyer.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-osd-evolution.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-pixel-timing.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-osd-spi-injector.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "pal-ntsc-color",
          "title": "PAL і NTSC: колірна квадратура і фазовий маятник",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-ntsc-pal-secam-war.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-pal-phase-pendulum.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-pal-demodulator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "adaptive-modulation",
          "title": "Адаптивна модуляція і кодування",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-amc-evolution.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-snr-mcs-thresholds.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-amc-loop.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "partial-band-jamming",
          "title": "Типи завад і протидія",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-ew-battle.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-ber-jamming.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-jamming-sim.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "fhss-sync",
          "title": "Синхронізація в FHSS-лінку",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-have-quick-sincgars.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-drift-bounds.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-fhss-sync-sim.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "baseband-passband",
          "title": "База й смугова область",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-superheterodyne.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-complex-envelope.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-iq-modulator-demodulator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "iq-representation",
          "title": "IQ-подання сигналу",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-iq-origin.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-iq-transform.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-iq-demodulator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "carson-rule",
          "title": "Правило Карсона",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-carson-armstrong.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-bessel-expansion.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-carson-spectrum-sim.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "chirp-coding",
          "title": "Чирп і кодований сигнал",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-radar-to-lora.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-pulse-compression.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-css-sim.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "carrier-ir-modulation",
          "title": "Модуляція несучої для відсіву перешкод (38 кГц як у ІЧ-пультах)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-ir-receiver.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-ir-remote-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-bandpass-snr.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-ir-nec-modem.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "qam",
          "title": "Квадратурна амплітудна модуляція (QAM)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-qam-evolution.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-qam-constellation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-qam-demodulator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "dsb-sc",
          "title": "Двосмугова модуляція з придушеною несучою (DSB-SC)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-balanced-modulator.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-ring-modulator.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-costas-loop.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-dsb-sc-sdr.md",
              "status": "done"
            }
          ]
        }
      ]
    },
    {
      "slug": "signal-processing",
      "title": "Обробка сигналів",
      "scope": "Перетворення, фільтрація та виявлення сигналів у цифровій і аналоговій формі.",
      "topics": [
        {
          "slug": "nyquist-aliasing",
          "title": "Найквіст і аліасинг",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-alias-folding.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "resolution-framerate",
          "title": "Роздільність і кадри",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "pn-sequences",
          "title": "PN-послідовності",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-golomb-m-sequences.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-lfsr-polynomials.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-pn-generator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "rake-receiver",
          "title": "RAKE-приймач",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-rake-invention.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-rake-combining.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-rake-demodulator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "sampling-reconstruction",
          "title": "Відновлення сигналу з відліків",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-whittaker-shannon.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-sinc-reconstruction.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-sinc-interpolator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "chroma-subsampling",
          "title": "Колірне субдискретування",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-yuv-color-tv.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-chroma-grid.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-chroma-converter.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "color-spaces-video",
          "title": "Колірні простори у відео",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-video-color-metadata.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-color-matrix-derivation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-color-space-converter.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "generation-loss",
          "title": "Втрата поколінь: накопичення похибки при копіюванні",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-magnetic-tape-cascade.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-noise-accumulation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-generation-cascade-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "ycbcr",
          "title": "Колірний простір YCbCr",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-yuv-to-ycbcr.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-ycbcr-conversion.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-ycbcr-fixedpoint.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "bandwidth",
          "title": "Смуга пропускання",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-3db-origin.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-enbw-derivation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-bandwidth-estimator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "h264-hardware-codec",
          "title": "Апаратний кодек H.264",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-v4l2-codec.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-h264-hardware.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-h264-transform.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-h264-cabac-pipeline.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "decimation",
          "title": "Проріджування (decimation): фільтр і зниження частоти відліків",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-multirate-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-decimation-spectrum.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-decimator-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "sensor-fusion",
          "title": "Сенсорне злиття (fusion): комплементарний фільтр і Калман",
          "basic": {
            "status": "recheck",
          "math": [
            {
              "file": "math-gaussian-fusion.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-fusion-compare-c.md",
              "status": "recheck"
            }
          ],
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-gaussian-fusion.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-fusion-compare-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "analytic-signal",
          "title": "Аналітичний сигнал і перетворення Гільберта",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-hilbert-transform.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-hilbert-properties.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-hilbert-transform.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "interpolation-upsampling",
          "title": "Інтерполяція (upsampling): вставлення нулів і згладжувальний фільтр",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-polyphase-birth.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-spectral-imaging.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-interpolator-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "channel-equalization",
          "title": "Вирівнювання каналу: zero-forcing і MMSE",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-equalizer-history.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-mmse-derivation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-equalizer-sim.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "media-container",
          "title": "Медіаконтейнер: як стиснені кадри складають у файл",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-container-demux.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-mp4-mpegts.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-pts-dts-drift.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-mp4-parser.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "speech-codecs",
          "title": "Мовні кодеки: G.711, G.729, Opus",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-opus-encoder.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-speech-codecs.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-lpc-acelp.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-g711-codec.md",
              "status": "done"
            }
          ]
        }
      ]
    },
    {
      "slug": "propagation",
      "title": "Поширення хвиль",
      "scope": "Поведінка електромагнітних хвиль у середовищі: загасання, відбиття, завмирання, дальність.",
      "topics": [
        {
          "slug": "propagation-polarization",
          "title": "Поширення й поляризація",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "frequency-bands",
          "title": "Діапазони частот",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "power-decibels",
          "title": "Потужність і децибели",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-decibel-origin.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-log-decibel.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "free-space-loss",
          "title": "Загасання у просторі",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-fspl-derivation.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "multipath-fading",
          "title": "Багатопроменевість",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-rayleigh-fading.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "ism-bands",
          "title": "ISM-діапазони",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-ism-allocation.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-duty-cycle.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-lbt-simulator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "friis-transmission",
          "title": "Рівняння Фріїса",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-friis-origin.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-friis-derivation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-friis-calculator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "ionospheric-propagation",
          "title": "Іоносферне поширення",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-heaviside-kennelly.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-plasma-frequency.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-ionosphere-muf-calculator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "atmospheric-absorption",
          "title": "Атмосферне поглинання хвиль",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-atmospheric-absorption.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-van-vleck-weisskopf.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-atmospheric-calculator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "fresnel-zones",
          "title": "Зони Френеля й умова вільного простору",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-fresnel-discovery.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-fresnel-derivation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-fresnel-calculator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "fading-statistics",
          "title": "Статистика завмирань: Релей, Раєна, Накагамі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-fading-statistics.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-fading-distributions.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-fading-simulator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "delay-spread",
          "title": "Delay spread і когерентна смуга",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-delay-spread.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-pdp-moments.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-pdp-calculator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "db-reference-variants",
          "title": "Варіанти децибельних одиниць (dBW, dBc, dBFS, dBu…)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-reference-origins.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-db-conversions.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-db-calculator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "rssi-signal-strength",
          "title": "RSSI і вимірювання рівня сигналу",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-cellular-at-commands.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-rssi-origin.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-rsrp-rsrq-derivation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-rssi-filter-c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "link-quality-metrics",
          "title": "Метрики якості лінку",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-link-metrics-parser.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-ber-testing.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-ber-snr-derivation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-link-monitor.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "link-budget",
          "title": "Бюджет лінку",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-link-budget-lib.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-link-budget.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-link-budget.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-link-budget-calc.md",
              "status": "done"
            }
          ]
        }
      ]
    },
    {
      "slug": "antennas",
      "title": "Антени",
      "scope": "Випромінювання й приймання хвиль: діаграми спрямованості, підсилення, апертури, решітки.",
      "topics": [
        {
          "slug": "antenna",
          "title": "Антена",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-marconi.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "resonance-dipole",
          "title": "Резонанс і диполь",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "antenna-gain",
          "title": "Підсилення антени",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "antenna-polarization",
          "title": "Поляризація антени",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-mismatch.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "radiation-pattern-3d",
          "title": "Тривимірна діаграма спрямованості",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-vtu-export.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-3d-directivity.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-pattern-integrator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "directivity",
          "title": "Спрямованість антени",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-kraus.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-directivity.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "effective-aperture",
          "title": "Ефективна апертура антени",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-aperture.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-aperture-gain.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-aperture-calculator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "parabolic-antenna",
          "title": "Параболічна антена",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-feed-types.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-grote-reber.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-parabola-phase.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-pattern-sim.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "yagi-uda-antenna",
          "title": "Антена Яґі-Уда",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-yagi-matching.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-yagi-uda.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-yagi-uda.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-yagi-calc.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "helix-antenna",
          "title": "Спіральна антена",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-axial-helix.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-kraus.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-helix-geometry.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-helix-calc.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "polarization-diversity",
          "title": "Поляризаційне різноманіття",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-dual-slant-antenna.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-diversity-gain.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-diversity-sim.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "antenna-impedance-matching",
          "title": "Узгодження імпедансу антени",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-matching-components.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-smith-chart.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-l-network.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-l-match-calc.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "antenna-feed",
          "title": "Живлення антен: балун, гама-узгоджувач, узгодження імпедансів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-balun-chokes.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-balun-evolution.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-gamma-match.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-gamma-match-calc.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "loading-coil",
          "title": "Завантажувальна котушка: укорочення антени індуктивністю",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-loading-coil.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-coil-design.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-coil-calc.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "radiation-resistance",
          "title": "Опір випромінювання антени",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-antenna-loss.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-radiation-resistance.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-dipole-radiation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-rad-resistance-calc.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "circular-polarization",
          "title": "Кругова та еліптична поляризація",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-cp-generators.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-polarization-discovery.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-polarization-ellipse.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-polarization-analyzer.md",
              "status": "done"
            }
          ]
        }
      ]
    },
    {
      "slug": "radio-engineering",
      "title": "Радіотехніка",
      "scope": "Схемотехніка приймачів і передавачів: підсилювачі, змішувачі, гетеродини, синтезатори.",
      "topics": [
        {
          "slug": "rf-module",
          "title": "Радіомодуль",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-tcxo-reference.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-rf-modularization.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-cascade-noise-figure.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-rf-module-driver.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "rf-amplifiers",
          "title": "Радіочастотні підсилювачі (LNA і PA)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-rf-front-end.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-rf-amplifiers.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-friis-noise.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-lna-pa-control.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "mixer",
          "title": "Змішувач частот",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-mixer-config.md",
              "status": "done"
            }
          ],
          "comp": [
            {
              "file": "comp-active-passive-mixers.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-mixer-evolution.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-intermodulation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-sdr-mixer.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "local-oscillator",
          "title": "Гетеродин",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-tcxo-ocxo.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-fessenden-heterodyne.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-reciprocal-mixing.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-pll-lo-calc.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "lora",
          "title": "LoRa",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "superheterodyne",
          "title": "Супергетеродин",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "transmission-lines",
          "title": "Лінії передачі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "vswr",
          "title": "Відбиття і КСХ",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "telemetry-link",
          "title": "Канал земля-борт",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-rf-frontend.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "emc-certification",
          "title": "Модульна сертифікація: FCC, CE та EMC-випроби",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-spectrum-order.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "nfc-protocols",
          "title": "Протоколи NFC: ISO 14443, NDEF і режими роботи",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-iso14443-commands.md",
              "status": "done"
            }
          ],
          "comp": [
            {
              "file": "comp-nfc-controller-frontend.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-nfc-standardization.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-load-modulation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-ndef-parser-builder.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "rfid-security",
          "title": "Безпека NFC/RFID: атаки та захист",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-iso14443-crypto-frame.md",
              "status": "done"
            }
          ],
          "comp": [
            {
              "file": "comp-nfc-secure-element.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-mifare-crypto1.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-relay-distance-bounding.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-nfc-relay-emulator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "double-conversion",
          "title": "Подвійне перетворення частоти",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-dual-conversion-receiver.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-double-conversion.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-frequency-planning.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-frequency-planner.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "zero-if-receiver",
          "title": "Zero-IF та Low-IF архітектури",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-zero-low-if.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-direct-conversion.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-iq-imbalance.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-dcoc-iq-calib.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "frequency-synthesizer",
          "title": "Синтезатор частоти",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-synthesizer-control.md",
              "status": "done"
            }
          ],
          "comp": [
            {
              "file": "comp-pll-dds-synthesizers.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-frequency-synthesizer.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-pll-synthesizer.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-pll-synthesizer-calc.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "impedance-matching-networks",
          "title": "Мережі узгодження імпедансу",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-rf-matching.md",
              "status": "done"
            }
          ],
          "comp": [
            {
              "file": "comp-matching-topologies.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-matching-networks.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-l-network.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-l-network-calc.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "smith-chart",
          "title": "Діаграма Сміта",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-smith-transform.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-smith-calculator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "tdr",
          "title": "Рефлектометрія у часовій області (TDR)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-tdr-scpi.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-tdr-radar-origins.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-reflection-impedance.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-tdr-analyzer.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "return-loss",
          "title": "Зворотні втрати (return loss)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "math": [
            {
              "file": "math-return-loss-conversions.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-return-loss-vna.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "balun",
          "title": "Балун",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-ferrite-baluns.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-balun-evolution.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-mode-decomposition.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-balun-designer.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "time-on-air",
          "title": "Час у ефірі (time on air)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-sx126x-toa.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-duty-cycle.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-toa-equations.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-toa-calculator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "reflection-coefficient",
          "title": "Коефіцієнт відбиття",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-directional-coupler.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-reflection-coefficient.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-gamma-derivation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-gamma-calculator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "elrs-architecture",
          "title": "Архітектура ExpressLRS",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-elrs-origin.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "wifi-6-basics",
          "title": "Wi-Fi 6: ключові ідеї",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-nl80211-he-config.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-wifi6-evolution.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-ofdma-ru-timing.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-wifi6-ru-scheduler.md",
              "status": "done"
            }
          ]
        }
      ]
    },
    {
      "slug": "photonics",
      "title": "Фотоніка",
      "scope": "Передача світлом по волокну й у вільному просторі: лазери, детектори, дисперсія, підсилювачі.",
      "topics": [
        {
          "slug": "optical-fiber",
          "title": "Оптоволокно",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "fiber-in-network",
          "title": "Оптоволокно в мережі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-sfp-dom.md",
              "status": "done"
            }
          ],
          "comp": [
            {
              "file": "comp-optical-transceivers.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-optical-networking.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-optical-budget.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-link-budget-calc.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "wdm",
          "title": "Хвильове мультиплексування (WDM/DWDM)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-dwdm-grid.md",
              "status": "done"
            }
          ],
          "comp": [
            {
              "file": "comp-awg.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-wdm.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-wdm-capacity.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-wdm-sim.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "optical-amplifier",
          "title": "Оптичний підсилювач (EDFA)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-edfa.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-gain-saturation.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-edfa-sim.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "chromatic-dispersion",
          "title": "Хроматична дисперсія у волокні",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-dcf-module.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-zero-dispersion.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-dispersion-pulse.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-dispersion-calc.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "fiber-splicing",
          "title": "Зрощення та конектори оптоволокна",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-fusion-splicer.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-arc-fusion.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-splice-loss.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-otdr-trace.md",
              "status": "done"
            }
          ]
        }
      ]
    },
    {
      "slug": "networks",
      "title": "Мережі",
      "scope": "Топологія, комутація й маршрутизація потоків між вузлами в локальних і глобальних структурах.",
      "topics": [
        {
          "slug": "bgp-basics",
          "title": "BGP: протокол зв'язку між автономними системами",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-bgp-messages.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-bgp-origins.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-bgp-peering.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "stp-rstp",
          "title": "Spanning Tree Protocol (STP) та Rapid Spanning Tree Protocol (RSTP): захист від мережевих петель у комутованих мережах L2",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-bpdu-frame.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-spanning-tree.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-rstp-state-machine.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "vlan-and-trunking",
          "title": "VLAN та транкінг",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-8021q-header.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-vlan-history.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-vlan-handling.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "utp-cable",
          "title": "UTP-кабель",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "on-chip-radio",
          "title": "Радіо на чіпі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-bluetooth-name.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "channel-band-packet",
          "title": "Канал і пакет",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-listen-before-talk.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "wifi",
          "title": "Wi-Fi",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-wifi-name.md",
              "status": "done"
            },
            {
              "file": "hist-csiro-ofdm.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "bluetooth-spp",
          "title": "Bluetooth SPP",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-command-parser.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "esp-now",
          "title": "ESP-NOW",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "latency-reliability",
          "title": "Затримка й надійність",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "video-transmission",
          "title": "Передача відео",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "bandwidth-loss",
          "title": "Пропускна й втрати",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "ethernet-frame",
          "title": "Кадр Ethernet",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-frame-headers.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-dix-to-ieee.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-frame-parser.md",
              "status": "recheck"
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
          "slug": "ethernet-link-phy",
          "title": "Фізика лінка",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-phy-interfaces.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-mdio-driver.md",
              "status": "recheck"
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
          "slug": "mac-ip-arp",
          "title": "MAC, IP і ARP",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "ip-routing",
          "title": "Маршрутизація",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "dhcp-dns",
          "title": "DHCP і DNS",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-dhcp-options-dns-records.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-bootp-and-hosts.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-dns-client.md",
              "status": "recheck"
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
          "slug": "nat",
          "title": "NAT",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-nat-evolution.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-checksum-update.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-conntrack-nat.md",
              "status": "recheck"
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
          "slug": "shannon-capacity",
          "title": "Ємність каналу за Шенноном",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-shannon-hartley.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-shannon-limit.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-link-budget-capacity.md",
              "status": "recheck"
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
          "slug": "fec-codes",
          "title": "Коди виправлення помилок (FEC)",
          "basic": {
            "status": "empty",
          "comp": [
            {
              "file": "comp-fec-families.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-shannon-to-polar.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-coding-gain.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-fec-pipeline.md",
              "status": "recheck"
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
          "slug": "queue-theory-networks",
          "title": "Черги в мережах: затримка і втрати",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-bufferbloat.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-pollaczek-khinchine.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-codel-simulation.md",
              "status": "recheck"
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
          "slug": "gilbert-elliott-channel",
          "title": "Модель каналу Гілберта–Елліота",
          "basic": {
            "status": "empty",
          "math": [
            {
              "file": "math-markov-channel.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-burst-harq-sim.md",
              "status": "recheck"
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
          "slug": "bluetooth-classic-stack",
          "title": "Стек Bluetooth Classic",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-hci-uart.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-fhss-slots.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-l2cap-sar.md",
              "status": "recheck"
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
          "slug": "bt-pairing-security",
          "title": "Безпека спарювання Bluetooth",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-pairing-matrix.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-pairing-evolution.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-pairing-crypto.md",
              "status": "recheck"
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
          "slug": "rfcomm",
          "title": "RFCOMM",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-bluez-rfcomm.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-gsm-to-rfcomm.md",
              "status": "recheck"
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
          "slug": "guard-band-duplexing",
          "title": "Захисні смуги і дуплекс",
          "basic": {
            "status": "empty",
          "comp": [
            {
              "file": "comp-fdd-tdd.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-guard-period.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-spectral-mask-aclr.md",
              "status": "recheck"
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
          "slug": "cidr",
          "title": "CIDR і префікси",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-cidr-calc.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-classful-exhaustion.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-radix-lpm.md",
              "status": "recheck"
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
          "slug": "ospf",
          "title": "OSPF: протокол стану каналів",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-ospf-packets.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-ospf-origins.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-spf-dijkstra.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-ospf-lab.md",
              "status": "recheck"
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
          "slug": "bgp",
          "title": "BGP: протокол між провайдерами",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-bgp-attributes.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-bgp-best-path.md",
              "status": "recheck"
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
          "slug": "ipv6-routing",
          "title": "Маршрутизація IPv6",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-ndp-icmpv6.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-ipv6-birth.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-ndp-neighbor-probe.md",
              "status": "recheck"
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
          "slug": "jitter",
          "title": "Джитер: варіація затримки",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-rtcp-jitter.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-rtp-jitter.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-jitter-buffer.md",
              "status": "recheck"
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
          "slug": "arp-security",
          "title": "Безпека ARP",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-arp-frame.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-arp-trust-model.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-arp-monitor.md",
              "status": "recheck"
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
          "slug": "subnet-addressing",
          "title": "Адресація підмереж",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-rfc950-subnetting.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-vlsm-geometry.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-vlsm-allocator.md",
              "status": "recheck"
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
          "slug": "csma-ca",
          "title": "CSMA/CA: уникнення колізій у спільному ефірі",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-frame-control-nav.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-maca-80211.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-backoff-throughput.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-csma-simulator.md",
              "status": "recheck"
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
          "slug": "csma-cd",
          "title": "CSMA/CD: колізії у спільному дроті Ethernet",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-ethernet-origins.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-slot-time.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-csma-simulation.md",
              "status": "recheck"
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
          "slug": "poe",
          "title": "PoE — живлення по витій парі",
          "basic": {
            "status": "empty",
          "comp": [
            {
              "file": "comp-pd-interface.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-poe-origins.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-cable-heating.md",
              "status": "recheck"
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
          "slug": "mdi-mdix",
          "title": "MDI/MDI-X і авто-погодження",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-autoneg-registers.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-link-monitor.md",
              "status": "recheck"
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
          "slug": "adaptive-bitrate",
          "title": "Адаптивний бітрейт (ABR)",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-manifest-formats.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-streaming-evolution.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-abr-algorithms.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-abr-engine.md",
              "status": "recheck"
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
          "slug": "wpa-security",
          "title": "WPA2 і WPA3: захист бездротового ефіру",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-wep-to-wpa.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-dragonfly-sae.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-wpa2-ptk-derivation.md",
              "status": "recheck"
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
          "slug": "dhcp",
          "title": "DHCP: динамічне призначення IP-адрес",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-dhcp-options.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-dhcp-evolution.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-dhcp-packet.md",
              "status": "recheck"
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
          "slug": "auto-negotiation",
          "title": "Автопогодження Ethernet",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-mii-registers.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-an-fsm.md",
              "status": "recheck"
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
          "slug": "anycast",
          "title": "Anycast і глобальне балансування",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-bgp-anycast-config.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-root-dns-anycast.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-maglev-consistent-hash.md",
              "status": "recheck"
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
          "slug": "ip-fragmentation-mtu",
          "title": "MTU і фрагментація IP",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-ip-fragmentation.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-fragmentation-evolution.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-ip-reassembly.md",
              "status": "recheck"
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
          "slug": "source-specific-multicast",
          "title": "Фільтрація за джерелом: IGMPv3, MLDv2 і SSM",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-igmpv3-mldv2-records.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-multicast-evolution.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-ssm-receiver.md",
              "status": "recheck"
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
          "slug": "mtu-and-fragmentation",
          "title": "MTU й фрагментація IP",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-tunnel-overhead.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-1500-bytes.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-pmtud-probe.md",
              "status": "recheck"
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
          "slug": "middleboxes",
          "title": "Проміжні коробки (middlebox): фаєрволи, проксі, кеші, транслятори на шляху пакета",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-middlebox-taxonomy.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-end-to-end-erosion.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-middlebox-probe.md",
              "status": "recheck"
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
          "slug": "circuit-vs-packet-switching",
          "title": "Комутація каналів проти комутації пакетів",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-switching-evolution.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-statistical-multiplexing.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-switching-simulation.md",
              "status": "recheck"
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
          "slug": "dns-srv-naptr",
          "title": "Записи DNS SRV і NAPTR: пошук сервера служби за іменем домену",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-srv-naptr-records.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-srv-resolver.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-service-location.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "svcb-https-records",
          "title": "Записи SVCB і HTTPS: параметри служби в одній відповіді DNS",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-svcb-https-params.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-svcb-https-evolution.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-svcb-parser.md",
              "status": "recheck"
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
          "slug": "pstn-e164",
          "title": "Телефонна мережа й нумерація E.164",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-isup-messages.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-pstn-evolution.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-enum-resolver.md",
              "status": "recheck"
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
          "slug": "happy-eyeballs",
          "title": "Happy Eyeballs: паралельні спроби IPv6 і IPv4",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-rfc8305-params.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-broken-ipv6.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-happy-eyeballs.md",
              "status": "recheck"
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
      "slug": "protocols",
      "title": "Протоколи",
      "scope": "Правила обміну й керування з'єднанням: стеки, рівні, контроль потоку й помилок.",
      "topics": [
        { slug: "sctp", title: "SCTP: протокол передачі з контролем потоку", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-socket-sctp.md", status: "recheck" }] , "hist": [{ file: "hist-sigtran-birth.md", status: "recheck" }] , "proj": [{ file: "proj-sctp-chat.md", status: "recheck" }] },
        {
          "slug": "http3-quic",
          "title": "HTTP/3 та QUIC: переосмислення мережевого стеку веб",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-quic-frame-spec.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-quic-gquic-to-rfc9000.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-quic-stream-multiplexer.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "tls-handshake",
          "title": "TLS Handshake: рукостискання й узгодження ключів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-tls-records.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-tls-evolution.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-hkdf-ecdhe.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-openssl-handshake.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "dns-sec",
          "title": "DNSSEC: цифровий підпис і ланцюг довіри в системі доменних імен",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-dnssec-records.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-dnssec.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-dnssec-crypto.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-dnssec-val.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "tcp-congestion-control",
          "title": "Керування заторами TCP",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-tcp-cc-socket.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-tcp-collapse.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-aimd-stability.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-cc-algo-sim.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "modbus",
          "title": "Modbus",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-modbus-functions.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-modicon-1979.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-modbus-rtu-parser.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "can-open",
          "title": "CANopen: від CAN-кадру до стандартизованого профілю пристрою",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-object-dictionary.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-cia.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-sdo-transfer.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "lin-bus",
          "title": "LIN Bus: локальна мережа автомобільних підсистем",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-lin-frame-spec.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-lin-consortium.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-lin-frame-parser.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "can-bus",
          "title": "CAN: від фізичного кадру до контролю помилок",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-can-frame-spec.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-can-bosch-1986.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-can-socket-filter.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "flexray",
          "title": "FlexRay: детермінована високошвидкісна шина для критичних систем",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-flexray-frame-registers.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-flexray-consortium.md",
              "status": "done"
            }
          ],
          "math": [
            {
              "file": "math-clock-sync.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-flexray-cycle-simulator.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "flow-control",
          "title": "Керування потоком",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-ring-buffer.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "packet-design",
          "title": "Проєктування пакета",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-crc-table.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "tcp-vs-udp",
          "title": "TCP проти UDP",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-headers.md",
              "status": "done"
            },
            {
              "file": "api-sockets.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "ble-gatt",
          "title": "BLE GATT",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-cccd-notify.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "reliable-link",
          "title": "Надійний обмін",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-stop-and-wait.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "mqtt",
          "title": "MQTT",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "control-telemetry",
          "title": "Керування й телеметрія",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-mavlink.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "rc-link",
          "title": "RC-лінк",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-sbus-decode.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "telemetry-stream",
          "title": "Телеметрія",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-telemetry-radio.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "mavlink-packet",
          "title": "Пакет MAVLink",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "mavlink-message-dictionary",
          "title": "Словник MAVLink",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-common-messages.md",
              "status": "recheck"
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "coordinate-frames-units",
          "title": "Координати й одиниці",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-mavlink-coordinates.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-rotations-dcm.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-frame-transform.md",
              "status": "recheck"
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
          "slug": "stream-rates",
          "title": "Частоти потоків",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-message-interval.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-bandwidth-budget.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-dynamic-throttling.md",
              "status": "recheck"
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
          "slug": "param-protocol",
          "title": "Протокол параметрів",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-param-messages.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-param-sync.md",
              "status": "recheck"
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
          "slug": "mission-protocol",
          "title": "Протокол місій",
          "basic": {
            "status": "empty",
          "math": [
            {
              "file": "math-coordinate-precision.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-mission-uploader.md",
              "status": "recheck"
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
          "slug": "mavlink-commands",
          "title": "Команди MAVLink",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "motion-control-setpoints",
          "title": "Керування рухом",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-mavlink-setpoints.md",
              "status": "recheck"
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "mavlink-pitfalls",
          "title": "Граблі MAVLink",
          "basic": {
            "status": "empty",
          "math": [
            {
              "file": "math-coordinate-precision.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-mavlink-uart-dma.md",
              "status": "recheck"
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
          "slug": "arq-protocol",
          "title": "ARQ: автоматичний повтор запиту",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-tcp-sack-fields.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-arq-evolution.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-channel-utilization.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-sliding-window.md",
              "status": "recheck"
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
          "slug": "ble-gap",
          "title": "BLE GAP",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-ad-structures.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-adv-parser.md",
              "status": "recheck"
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
          "slug": "ble-att",
          "title": "ATT-протокол BLE",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-att-pdus.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-att-parser.md",
              "status": "recheck"
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
          "slug": "ble-security",
          "title": "Безпека й спарювання BLE",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-smp-pdus.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-smp-crypto.md",
              "status": "recheck"
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
          "slug": "ble-beacon-formats",
          "title": "Формати BLE-маячків",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-beacon-payloads.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-rssi-ranging.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-beacon-parser.md",
              "status": "recheck"
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
          "slug": "mavlink-mission-protocol",
          "title": "Протокол місій MAVLink",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-mission-protocol.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-mission-uploader.md",
              "status": "recheck"
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
          "slug": "mavlink-parameters",
          "title": "Параметри MAVLink",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-param-protocol.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-param-sync.md",
              "status": "recheck"
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
          "slug": "mavlink-v2-signing",
          "title": "MAVLink v2 і підпис",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-signing-structures.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-signing-origin.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-packet-signer.md",
              "status": "recheck"
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
          "slug": "gcs-failsafe",
          "title": "Failsafe на стороні GCS",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-mavlink-failsafe.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-heartbeat-watchdog.md",
              "status": "recheck"
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
          "slug": "sequence-numbering",
          "title": "Нумерація послідовності пакетів",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-seq-protocols.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-sequence-numbers.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-sequence-arithmetic.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-reorder-buffer.md",
              "status": "recheck"
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
          "slug": "crsf-protocol",
          "title": "Протокол CRSF",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-crsf-origin.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-crsf-parser.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "rc-failsafe-modes",
          "title": "Режими failsafe RC",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-failsafe-origin.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "sliding-window-arq",
          "title": "ARQ зі ковзним вікном",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-hdlc-framing.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-sliding-window.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-window-limits.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-sliding-window.md",
              "status": "recheck"
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
          "slug": "quic-protocol",
          "title": "QUIC та HTTP/3",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-quic-frames.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-quic-evolution.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-rtt-loss-detection.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-quic-packet-parser.md",
              "status": "recheck"
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
          "slug": "nat-traversal",
          "title": "NAT-траверсаль",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-stun-turn-headers.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-traversal-evolution.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-ice-priority.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-udp-hole-punching.md",
              "status": "recheck"
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
          "slug": "lorawan",
          "title": "LoRaWAN",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-lorawan-mac-commands.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-lorawan-standard.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-adr-link-budget.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-lorawan-mic-cipher.md",
              "status": "recheck"
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
          "slug": "rc-signal-protocol",
          "title": "RC-сигнал: PWM, PPM і S.BUS",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-sbus-frame-parser.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "slip-protocol",
          "title": "Протокол SLIP: кадрування послідовного потоку",
          "basic": {
            "status": "empty",
          "comp": [
            {
              "file": "comp-framing-methods.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-slip-origin.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-slip-codec.md",
              "status": "recheck"
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
          "slug": "ble-link-layer",
          "title": "BLE Link Layer: канальний стрибок і connection events",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-ll-pdu.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-hopping-csa.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-ll-fsm-sim.md",
              "status": "recheck"
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
          "slug": "thread-mesh",
          "title": "Thread: IPv6-mesh для IoT",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-mle-tlv.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-thread-origins.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-openthread-node.md",
              "status": "recheck"
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
          "slug": "mavlink-mission-items",
          "title": "MAVLink: місія й команди польоту",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-mission-commands.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-mission-builder.md",
              "status": "recheck"
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
          "slug": "ntp-sync",
          "title": "NTP: мережевий протокол синхронізації часу",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-packet.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-david-mills.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-marzullo-intervals.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-sntp-client.md",
              "status": "recheck"
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
          "slug": "cobs-framing",
          "title": "Кадрування COBS",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-cobs-codec.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-cobs-origin.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-cobs-overhead.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-cobs-codec.md",
              "status": "recheck"
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
          "slug": "mavlink-dialect",
          "title": "Діалекти MAVLink",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-dialect-xml-schema.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-custom-dialect-integration.md",
              "status": "recheck"
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
          "slug": "regulatory-radio-certification",
          "title": "Радіосертифікація: FCC, CE, SRRC",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-certification-workflow.md",
              "status": "recheck",
          "comp": [
            {
              "file": "comp-regulatory-frameworks.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-spectrum-regulation.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-eirp-sar-budget.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-spurious-emissions-mask.md",
              "status": "recheck"
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
          "slug": "rtp-rtcp",
          "title": "RTP і RTCP: транспорт медіа поверх UDP",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-rtp-birth.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-packet-format.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-depacketizer.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "rtsp-sdp",
          "title": "RTSP і SDP: керування сеансом потокового відео",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-rtsp-reference.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-rtsp-client.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "mavlink-xml-codegen",
          "title": "Генерація коду з XML-опису MAVLink",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-crc-extra.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-mavgen.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "mavlink-camera-gimbal",
          "title": "Протоколи камери й підвісу MAVLink",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-camera-definition.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-gimbal-point-and-shoot.md",
              "status": "done"
            }
          ],
          "hist": [
            {
              "file": "hist-mount-to-gimbal-v2.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "mavlink-ftp",
          "title": "MAVFTP: передача файлів поверх MAVLink",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-mavftp-protocol.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-mavftp-client.md",
              "status": "recheck"
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
          "slug": "mavlink-high-latency",
          "title": "Протокол великої затримки MAVLink",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-high-latency-protocol.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-satellite-telemetry.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-latency-bandwidth.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-satellite-bridge.md",
              "status": "recheck"
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
          "slug": "mavlink-heartbeat",
          "title": "HEARTBEAT: як апарат оголошує себе",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-heartbeat-struct.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-heartbeat-monitor.md",
              "status": "recheck"
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
          "slug": "mavlink-capabilities",
          "title": "Можливості апарата: бітова маска AUTOPILOT_VERSION",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-autopilot-version.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-capabilities-negotiation.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-capability-parser.md",
              "status": "recheck"
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
          "slug": "mavlink-terrain-protocol",
          "title": "Протокол рельєфу MAVLink: TERRAIN_REQUEST, TERRAIN_DATA, TERRAIN_REPORT",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-terrain-protocol.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-terrain-interpolator.md",
              "status": "recheck"
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
          "slug": "mpeg-ts",
          "title": "MPEG-TS: транспортний потік як обгортка для ефіру",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-ts-psi-tables.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-mpeg-evolution.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-pcr-jitter.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-ts-demuxer.md",
              "status": "recheck"
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
          "slug": "mavlink-events-protocol",
          "title": "Протокол подій MAVLink: подія як ідентифікатор",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-events-protocol.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-event-decoder.md",
              "status": "recheck"
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
          "slug": "flight-log-formats",
          "title": "Формати бортових логів: ULog і DataFlash",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-ulog-dataflash-specs.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-log-buffering.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-flight-log-parser.md",
              "status": "recheck"
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
          "slug": "webrtc",
          "title": "WebRTC: медіа напряму між кінцевими вузлами",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-sdp-structure.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-webrtc-evolution.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-twcc-delay-gradient.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-webrtc-datachannel.md",
              "status": "recheck"
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
          "slug": "nmea-0183",
          "title": "NMEA 0183: речення супутникового приймача",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-nmea-sentences.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-nmea-origin.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-nmea-parser.md",
              "status": "recheck"
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
          "slug": "tcp-connection-lifecycle",
          "title": "Життєвий цикл TCP-з'єднання: встановлення, напівзакриття, TIME_WAIT",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-tcp-tunables.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-three-way-handshake.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-half-close.md",
              "status": "recheck"
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
          "slug": "sip",
          "title": "SIP: сигналізація сеансів зв'язку",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-sip-birth.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-sip-messages.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-invite-transaction.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "hls-dash",
          "title": "HLS і DASH: потокове відео сегментами поверх HTTP",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-hls-dash-birth.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-manifest-tags.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-hls-client.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "mavlink-component-id",
          "title": "Компоненти MAVLink: sysid, compid і адресація вузлів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-mavlink-router.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-component-ids.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "h323",
          "title": "H.323: телефонна сигналізація ITU-T поверх пакетних мереж",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-h323-vs-sip.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-h323-messages.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "enum-e164",
          "title": "ENUM: телефонний номер як ім'я в DNS",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-naptr-record.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-enum-evolution.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-enum-resolver.md",
              "status": "recheck"
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
          "slug": "isdn-q931",
          "title": "ISDN і сигналізація Q.931",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-q931-messages.md",
              "status": "recheck"
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "asn1-per",
          "title": "ASN.1 і правила кодування PER",
          "basic": {
            "status": "empty",
          "comp": [
            {
              "file": "comp-encoding-rules.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-integer-packing.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-per-bitstream.md",
              "status": "recheck"
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
          "slug": "cmaf",
          "title": "CMAF: один комплект сегментів для HLS і DASH",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-cmaf-boxes.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-cmaf-convergence.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-cmaf-parser.md",
              "status": "recheck"
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
          "slug": "osi-model",
          "title": "Семирівнева модель OSI: рівні, стос і чому він виявився важким",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-osi-pdu-structures.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-protocol-wars.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-clnp-parser.md",
              "status": "recheck"
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
      "slug": "multiple-access",
      "title": "Множинний доступ",
      "scope": "Спільне використання середовища багатьма абонентами через поділ ресурсу й арбітраж.",
      "topics": [
        {
          "slug": "clock-stretch-arbitration",
          "title": "Розтягування й арбітраж",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-clock-stretching-slave.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "cdma",
          "title": "CDMA: код як адреса",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-spread-spectrum.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-walsh-hadamard.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-dss-simulation.md",
              "status": "recheck"
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
          "slug": "mimo",
          "title": "MIMO",
          "basic": {
            "status": "empty",
          "comp": [
            {
              "file": "comp-mimo-modes.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-mimo-evolution.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-alamouti-2x2.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-mimo-capacity.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-mimo-detector.md",
              "status": "recheck"
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
          "slug": "ofdma",
          "title": "OFDMA: множинний доступ на ортогональних піднесних",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-ofdma-evolution.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-multiuser-diversity.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-ofdma-scheduler.md",
              "status": "recheck"
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
      "slug": "synchronization",
      "title": "Синхронізація",
      "scope": "Узгодження часу, частоти й фази між передавачем і приймачем, відновлення тактів.",
      "topics": [
        {
          "slug": "gnss",
          "title": "GNSS",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "baud-rate",
          "title": "Швидкість baud",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "measurement-time",
          "title": "Час вимірювання",
          "basic": {
            "status": "empty",
          "math": [
            {
              "file": "math-crlb-time-delay.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-coherent-integrator.md",
              "status": "recheck"
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
          "slug": "timestamps",
          "title": "Мітки часу",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-socket-timestamping.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-timestamp-conversion.md",
              "status": "recheck"
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
          "slug": "sampling-jitter",
          "title": "Джиттер вибірки",
          "basic": {
            "status": "empty",
          "math": [
            {
              "file": "math-jitter-snr.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-timer-triggered-adc.md",
              "status": "recheck"
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
          "slug": "synchronous-multi-sensor-read",
          "title": "Синхронне зчитування",
          "basic": {
            "status": "empty",
          "math": [
            {
              "file": "math-lagrange-resampling.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-sync-dma-trgo.md",
              "status": "recheck"
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
          "slug": "pps-pulse",
          "title": "PPS-імпульс",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-pps-origins.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-pps-input-capture.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "clock-offset-drift",
          "title": "Дрейф годинників",
          "basic": {
            "status": "empty",
          "math": [
            {
              "file": "math-allan-variance.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-clock-servo.md",
              "status": "recheck"
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
          "slug": "sensor-latency-compensation",
          "title": "Затримка давача",
          "basic": {
            "status": "empty",
          "math": [
            {
              "file": "math-phase-margin-loss.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-ekf-ring-buffer.md",
              "status": "recheck"
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
          "slug": "fractional-baud",
          "title": "Дробовий дільник baud",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-mcu-brr-registers.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-bresenham-accumulator.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-brr-calculator.md",
              "status": "recheck"
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
          "slug": "uart-oversampling",
          "title": "Передискретизація UART",
          "basic": {
            "status": "empty",
          "math": [
            {
              "file": "math-timing-budget.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-oversampling-receiver.md",
              "status": "recheck"
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
          "slug": "sbas-corrections",
          "title": "Супутникові системи доповнення (SBAS)",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-sbas-origins.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "leap-second",
          "title": "Високосна секунда",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-posix-leap-flags.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-leap-second-origins.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-leap-smear.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-leap-smear-slew.md",
              "status": "recheck"
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
          "slug": "ptp-1588",
          "title": "PTP (IEEE 1588): точна синхронізація часу в мережі",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-ptp-messages.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-ptp-origins.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-offset-delay.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-ptp-hw-timestamping.md",
              "status": "recheck"
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
      "slug": "cryptographic-comm",
      "title": "Криптозв'язок",
      "scope": "Захист конфіденційності, цілісності й автентичності переданих повідомлень.",
      "topics": [
        { slug: "sasl-framework", title: "Каркас автентифікації SASL (RFC 4422)", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-sasl-mechanisms.md", status: "recheck" }] , "hist": [{ file: "hist-sasl-evolution.md", status: "recheck" }] , "proj": [{ file: "proj-sasl-negotiation.md", status: "recheck" }] },
        {
          "slug": "mavlink-security",
          "title": "Безпека MAVLink",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-signing-spec.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-uav-security.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-secure-mavlink.md",
              "status": "recheck"
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
          "slug": "public-key-crypto",
          "title": "Криптографія з відкритим ключем: ключі, підпис, ланцюг сертифікатів",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-x509-asn1.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-public-key-revolution.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-trapdoor-functions.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-cert-chain-verify.md",
              "status": "recheck"
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
          "slug": "tls",
          "title": "TLS",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-record-wire.md",
              "status": "recheck",
          "comp": [
            {
              "file": "comp-tls12-vs-tls13.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-ssl-to-tls13.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-hkdf-keyschedule.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-record-codec.md",
              "status": "recheck"
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
          "slug": "hmac",
          "title": "HMAC і коди автентичності повідомлень",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-hmac-interfaces.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-mac-evolution.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-bck-security.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-hmac-impl.md",
              "status": "recheck"
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
          "slug": "srtp",
          "title": "SRTP: шифрування й автентичність медіапотоку",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-srtp-packet.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-srtp-evolution.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-srtp-crypto.md",
              "status": "recheck"
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
          "slug": "kerberos-authentication",
          "title": "Kerberos: квитки й автентифікація в мережі",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-kerberos-structures.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-kerberos-athena.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-ticket-verification.md",
              "status": "recheck"
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
          "slug": "digest-authentication",
          "title": "Дайджест-автентифікація: одноразове число, виклик і доказ без пароля в мережі",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-digest-birth.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-digest-client.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-digest-headers.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "common-encryption",
          "title": "Спільне шифрування медіа (CENC): одні сегменти, різні системи ключів",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-cenc-standard.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-cenc-boxes.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-cenc-decrypt.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "dnssec",
          "title": "DNSSEC: підписи зони і ланцюг довіри до відповіді DNS",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-dnssec-records.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-kaminsky-attack.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-nsec3-hash.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-dnssec-val.md",
              "status": "recheck"
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
          "slug": "challenge-response",
          "title": "Виклик-відповідь: доказ знання секрету без його передавання",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-challenge-protocols.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-identification-friend-foe.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-zkp-schnorr.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-challenge-auth.md",
              "status": "recheck"
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
          "slug": "scram",
          "title": "SCRAM: солений виклик-відповідь, що не лишає ключа на сервері",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-scram-protocol.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-scram-evolution.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-scram-exchange.md",
              "status": "recheck"
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
          "slug": "drm-key-delivery",
          "title": "DRM: як ключ контенту потрапляє в пристрій",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-eme-interfaces.md",
              "status": "recheck",
          "comp": [
            {
              "file": "comp-tee-secure-path.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-drm-wars.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-license-exchange.md",
              "status": "recheck"
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
          "slug": "scram-authentication",
          "title": "SCRAM: солений виклик-відповідь замість дайджесту",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-scram-attributes.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-scram-standard.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-scram-crypto.md",
              "status": "recheck"
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
          "slug": "aead",
          "title": "AEAD: шифрування, що водночас доводить автентичність",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-aead-evolution.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-gcm-ghash.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-aead-packet.md",
              "status": "recheck"
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
          "slug": "authenticated-encryption",
          "title": "Автентифіковане шифрування (AEAD): тег, асоційовані дані й одна операція замість двох",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-composition-flaws.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-ghash-poly1305.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-aead-packet.md",
              "status": "recheck"
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
          "slug": "pkcs7-signed-message",
          "title": "PKCS#7/CMS: підписане повідомлення як самоописовий контейнер",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-cms-asn1.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-cms-evolution.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-pkcs7-sign-verify.md",
              "status": "recheck"
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
      "slug": "buses",
      "title": "Шини",
      "scope": "Провідний обмін між пристроями на коротких відстанях: послідовні й паралельні інтерфейси.",
      "topics": [
        {
          "slug": "i2c-expander",
          "title": "I²C-розширювач",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-register-architecture.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-interrupt-driver.md",
              "status": "recheck"
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
          "slug": "usb-c-connector",
          "title": "USB-C конектор",
          "basic": {
            "status": "recheck"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "async-serial",
          "title": "Асинхронна передача",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-baudot.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "uart-frame",
          "title": "Кадр UART",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-frame-in-code.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "i2c-bus",
          "title": "Шина I2C",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-i2c.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "i2c-addressing",
          "title": "Адресація I2C",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-i2c-mux.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-i2c-mux-scan.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "start-stop-ack",
          "title": "Старт, стоп, ACK",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-ack-handling.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "i2c-transaction",
          "title": "Транзакція I2C",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "register-map",
          "title": "Регістрова карта",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "proj": [
            {
              "file": "proj-sensor-driver.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "spi-bus",
          "title": "Шина SPI",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-spi.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-spi-transfer.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "spi-lines",
          "title": "Лінії SPI",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "comp": [
            {
              "file": "comp-tri-state-buffer.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "cpol-cpha",
          "title": "Режими CPOL/CPHA",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-motorola-spi.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "chip-select",
          "title": "Вибір кристала",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "spi-speed",
          "title": "Швидкість SPI",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "single-ended-line-limits",
          "title": "Межі односторонніх ліній",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "differential-pair",
          "title": "Диференційна пара",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "rs-485",
          "title": "RS-485",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "can-arbitration",
          "title": "Арбітраж CAN",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-can-bosch.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "can-frame-errors",
          "title": "Кадр CAN",
          "basic": {
            "status": "empty",
          "math": [
            {
              "file": "math-can-bit-timing.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-socketcan-error-handling.md",
              "status": "recheck"
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
          "slug": "dronecan",
          "title": "DroneCAN",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-uavcan-split.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "usb-ethernet-differential",
          "title": "USB та Ethernet пари",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "bus-resource-conflicts",
          "title": "Конфлікти шин",
          "basic": {
            "status": "empty",
          "proj": [
            {
              "file": "proj-i2c-bus-recovery.md",
              "status": "recheck"
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "baud-vs-bitrate",
          "title": "Baud проти біт/с",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-baudot-and-hartley.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-nyquist-shannon-capacity.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-baud-bitrate-calc.md",
              "status": "recheck"
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
          "slug": "clock-tolerance-uart",
          "title": "Допуск годинника UART",
          "basic": {
            "status": "empty",
          "math": [
            {
              "file": "math-baud-error-budget.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-brr-error-calc.md",
              "status": "recheck"
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
          "slug": "break-signal-uart",
          "title": "Break-сигнал UART",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-break-control.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-break-key.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-break-detection.md",
              "status": "recheck"
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
          "slug": "half-duplex-uart",
          "title": "Напівдуплекс UART",
          "basic": {
            "status": "empty",
          "comp": [
            {
              "file": "comp-rs485-transceiver.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-turnaround-timing.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-stm32-halfduplex-de.md",
              "status": "recheck"
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
          "slug": "spi-cs-timing",
          "title": "Часові параметри CS у SPI",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-timing-params.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-timing-budget.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-stm32-dma-cs.md",
              "status": "recheck"
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
          "slug": "spi-timing",
          "title": "Тайминг SPI: t_su, t_h, t_clk",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-spi-timings.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-timing-budget.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-timing-calculator.md",
              "status": "recheck"
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
          "slug": "spi-multimaster",
          "title": "SPI з кількома веденими і режимами",
          "basic": {
            "status": "empty",
          "math": [
            {
              "file": "math-bus-capacitance.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-dynamic-reconfig.md",
              "status": "recheck"
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
          "slug": "termination",
          "title": "Термінування ліній передачі",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-heaviside-reflections.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-reflection.md",
              "status": "recheck"
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
          "slug": "i2c-multimaster",
          "title": "Кілька ведучих на I2C",
          "basic": {
            "status": "empty",
          "proj": [
            {
              "file": "proj-multimaster-arbitration.md",
              "status": "recheck"
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "i2c-10bit-addressing",
          "title": "10-бітна адресація I2C",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-10bit-protocol.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-10bit-transfer.md",
              "status": "recheck"
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
          "slug": "i2c-speeds",
          "title": "Режими швидкості I2C",
          "basic": {
            "status": "empty",
          "comp": [
            {
              "file": "comp-active-accelerator.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-rc-timing.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-timing-calc.md",
              "status": "recheck"
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
          "slug": "smbus-protocol",
          "title": "Протокол SMBus",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-transactions.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-smbus.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-pec-crc8.md",
              "status": "recheck"
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
          "slug": "burst-read",
          "title": "Пакетне зчитування регістрів",
          "basic": {
            "status": "empty",
          "math": [
            {
              "file": "math-bus-overhead.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-dma-burst.md",
              "status": "recheck"
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
          "slug": "drdy-pattern",
          "title": "Шаблон DRDY і переривання давача",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "fifo-register",
          "title": "FIFO-регістри в давачах",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-fifo-registers.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-burst-dma-reader.md",
              "status": "recheck"
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
          "slug": "rs-422",
          "title": "RS-422",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-pinout-and-signals.md",
              "status": "recheck",
          "comp": [
            {
              "file": "comp-differential-interfaces.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-v11-standardization.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-rs422-transceiver.md",
              "status": "recheck"
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
          "slug": "spi-modes",
          "title": "Режими SPI (CPOL/CPHA)",
          "basic": {
            "status": "empty",
          "proj": [
            {
              "file": "proj-spi-bitbang.md",
              "status": "recheck"
            }
          ],
          },
          "detailed": {
            "status": "recheck"
          }
        },
        {
          "slug": "daisy-chain-spi",
          "title": "Daisy-chain у SPI",
          "basic": {
            "status": "empty",
          "comp": [
            {
              "file": "comp-daisy-architectures.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-shift-cascade.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-cascade-driver.md",
              "status": "recheck"
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
          "slug": "qspi-multi-lane",
          "title": "QSPI та багатолінійний SPI",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-qspi-protocol.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-jedec-sfdp.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-stm32-qspi-xip.md",
              "status": "recheck"
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
          "slug": "clock-stretching",
          "title": "Clock stretching у I2C",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-clock-stretching.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-bitbang-stretching.md",
              "status": "recheck"
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
          "slug": "i2c-clock-stretching",
          "title": "Розтягування такту I2C",
          "basic": {
            "status": "empty",
          "comp": [
            {
              "file": "comp-bidirectional-isolators.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-timing-throughput.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-bitbang-master.md",
              "status": "recheck"
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
          "slug": "smbus",
          "title": "SMBus",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-electrical-timing.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-sbs-if.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-smbalert-ara.md",
              "status": "recheck"
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
          "slug": "i2s-bus",
          "title": "Шина I2S",
          "basic": {
            "status": "empty"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-i2s.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-i2s-transmit.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "mdi-mdio-bus",
          "title": "Шина MDC/MDIO",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-clause22-clause45-registers.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-mii-management.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-mdio-bitbang.md",
              "status": "recheck"
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
          "slug": "sd-card-protocol",
          "title": "Протокол SD/SDIO",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-sd-commands.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-sd-card.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-sd-crc.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-sd-driver.md",
              "status": "recheck"
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
          "slug": "i2c-bus-timing",
          "title": "Часові діаграми I²C: START, STOP, ACK і clock stretching",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-um10204-timings.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-clock-sync.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-timing-margins.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-bitbang-timing.md",
              "status": "recheck"
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
          "slug": "i2c-bus-capacity",
          "title": "Ємність шини I²C і вибір підтяжок",
          "basic": {
            "status": "empty",
          "math": [
            {
              "file": "math-pullup-limits.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-pullup-calculator.md",
              "status": "recheck"
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
          "slug": "sdio-bus",
          "title": "Шина SDIO",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-sdio-linux.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-sdio-evolution.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-sdio-driver.md",
              "status": "recheck"
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
          "slug": "quad-spi",
          "title": "Quad-SPI (QSPI)",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-controller-registers.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-xip-cache-integration.md",
              "status": "recheck"
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
          "slug": "usb3-physical",
          "title": "USB 3.x фізично: SuperSpeed і вище",
          "basic": {
            "status": "empty",
          "hist": [
            {
              "file": "hist-superspeed.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-receiver-detect.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-8b10b-disparity.md",
              "status": "recheck"
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
          "slug": "usb-device-basics",
          "title": "Пристрій на шині USB: хост, енумерація, кінцеві точки, класи",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "recheck"
          },
          "api": [
            {
              "file": "api-standard-requests.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-descriptor-parser.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "one-wire",
          "title": "1-Wire — шина на одному дроті",
          "basic": {
            "status": "pending"
          },
          "detailed": {
            "status": "recheck"
          },
          "hist": [
            {
              "file": "hist-dallas-ibutton.md",
              "status": "done"
            }
          ],
          "api": [
            {
              "file": "api-onewire-reference.md",
              "status": "done"
            }
          ],
          "proj": [
            {
              "file": "proj-rom-search.md",
              "status": "done"
            },
            {
              "file": "proj-bitbang-master.md",
              "status": "done"
            }
          ]
        },
        {
          "slug": "i3c",
          "title": "Шина I3C",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-i3c-ccc.md",
              "status": "recheck",
          "hist": [
            {
              "file": "hist-mipi-i3c.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-i3c-throughput.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-i3c-controller.md",
              "status": "recheck"
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
      "slug": "radio",
      "title": "Радіо",
      "scope": "Радіочастотні діапазони, канальні плани й бездротові лінки конкретних застосувань.",
      "topics": [
        {
          "slug": "fpv-channels",
          "title": "Канали 5.8 ГГц для FPV (Raceband і смуги A/B/E/F)",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-bands.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-imd.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-freq-planner.md",
              "status": "recheck"
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
      "slug": "reliability",
      "title": "Надійність",
      "scope": "Забезпечення доставки попри помилки й втрати: повтори, підтвердження, відновлення зв'язку.",
      "topics": [
        {
          "slug": "arq",
          "title": "ARQ: автоматичний запит на повтор",
          "basic": {
            "status": "empty",
          "api": [
            {
              "file": "api-harq-mac.md",
              "status": "recheck",
          "math": [
            {
              "file": "math-throughput-efficiency.md",
              "status": "recheck",
          "proj": [
            {
              "file": "proj-arq-simulator.md",
              "status": "recheck"
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
    }
  ]
});
