.venv/bin/nuitka --follow-imports --enable-plugin=pyqt6 \
    --include-data-dir=src/frontend=frontend \
    --include-data-dir=src/assets=assets \
    --include-data-files=src/as-cmd=as-cmd \
    --standalone src/main.py
