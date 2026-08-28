python3 -m venv .venv-mavgen
. .venv-mavgen/bin/activate
pip install pymavlink

git clone https://github.com/mavlink/mavlink.git
cd mavlink

PYTHONHASHSEED=0 python -m pymavlink.tools.mavgen \
    --lang=C --wire-protocol=2.0 \
    --output=/tmp/mavlink-headers \
    message_definitions/v1.0/all.xml
