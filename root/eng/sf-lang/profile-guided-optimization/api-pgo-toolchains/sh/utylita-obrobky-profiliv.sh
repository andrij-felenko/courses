# Базове злиття кількох файлів сирих профілів в єдиний індексований файл
llvm-profdata merge -output=code.profdata input1.profraw input2.profraw

# Злиття з ваговими коефіцієнтами для комбінування денного та нічного навантаження
llvm-profdata merge -weighted-input=8,day_read.profdata \
                    -weighted-input=2,night_write.profdata \
                    -output=production_blend.profdata

# Експорт бінарного профілю у текстовий вигляд для ручного аналізу
llvm-profdata merge -text -output=profile.txt code.profdata
