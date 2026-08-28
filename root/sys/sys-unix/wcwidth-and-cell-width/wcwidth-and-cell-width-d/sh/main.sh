#!/usr/bin/env bash
# Тестова сітка перевірки ширини символів термінала

printf "Колонки:  |12345678901234567890|\n"
printf "ASCII:    |%-20s|\n" "Hello World!"
printf "Кирилиця: |%-20s|\n" "Привіт, світе!"
printf "CJK Wide: |%-20s|\n" "言語処理 (NLP)"
printf "Accent:   |%-20s|\n" "е́кранний тест"
printf "Emoji:    |%-20s|\n" "🚀 ракета"
printf "ZWJ Емод: |%-20s|\n" "👨‍💻 розробник"
printf "Прапор:   |%-20s|\n" "🇺🇦 Україна"
