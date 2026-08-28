#!/usr/bin/env python3
"""CI-скрипт діагностики часу збірки та агрегації результатів ftime-trace."""
import subprocess
import sys
import os
import shutil

def run_build_profiling(build_dir):
    print("=== Крок 1: Конфігурація та чиста збірка з -ftime-trace ===")
    os.makedirs(build_dir, exist_ok=True)
    
    # Генерація Ninja-проєкту з прапорцем трасування Clang
    cmake_cmd = [
        "cmake", "-B", build_dir, "-G", "Ninja",
        "-DCMAKE_CXX_COMPILER=clang++",
        "-DCMAKE_CXX_FLAGS=-ftime-trace",
        "-DCMAKE_BUILD_TYPE=Release"
    ]
    subprocess.run(cmake_cmd, check=True)
    
    # Повне очищення перед вимірюванням
    subprocess.run(["ninja", "-C", build_dir, "-t", "clean"], check=True)
    
    # Запуск повної збірки
    subprocess.run(["ninja", "-C", build_dir], check=True)
    
    print("=== Крок 2: Агрегація даних через ClangBuildAnalyzer ===")
    cba_binary = shutil.which("ClangBuildAnalyzer")
    if not cba_binary:
        print("Помилка: ClangBuildAnalyzer не знайдено у PATH!")
        sys.exit(1)
        
    trace_archive = os.path.join(build_dir, "build_trace_data.bin")
    
    # Збирання всіх окремих .json файлів трасування у бінарний архів
    subprocess.run([cba_binary, "--all", build_dir, trace_archive], check=True)
    
    # Генерація фінального текстового аналітичного звіту
    analysis = subprocess.run([cba_binary, "--analyze", trace_archive],
                              capture_output=True, text=True, check=True)
    
    report_output_path = os.path.join(build_dir, "build_speed_report.txt")
    with open(report_output_path, "w", encoding="utf-8") as f:
        f.write(analysis.stdout)
        
    print(analysis.stdout)
    print(f"\nЗвіт профілювання збережено: {report_output_path}")

if __name__ == "__main__":
    run_build_profiling("build_profile_ci")
