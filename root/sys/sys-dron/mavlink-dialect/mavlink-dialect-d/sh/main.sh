# Генерація C-кодека (header-only бібліотека) для кастомного діалекту
python -m pymavlink.tools.mavgen \
    --lang=C \
    --wire-protocol=2.0 \
    --output=generated/c/my_payload \
    my_payload.xml

# Генерація Python-кодека (модуль для pymavlink)
python -m pymavlink.tools.mavgen \
    --lang=Python \
    --wire-protocol=2.0 \
    --output=generated/python/my_payload.py \
    my_payload.xml
