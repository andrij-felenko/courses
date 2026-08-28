# Встановлення офіційних інструментів генерації
pip install pymavlink future

# Генерація C/C++ header-only бібліотеки для мікроконтролера
python -m pymavlink.tools.mavgen \
    --lang=C \
    --wire-protocol=2.0 \
    --output=generated/c_mavlink \
    smart_multispectral.xml

# Генерація модуля Python для тестового стенда
python -m pymavlink.tools.mavgen \
    --lang=Python \
    --wire-protocol=2.0 \
    --output=generated/python/smart_multispectral.py \
    smart_multispectral.xml
