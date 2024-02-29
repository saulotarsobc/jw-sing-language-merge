#! bash
pyinstaller \
    --log-level=INFO \
    --onefile \
    --console \
    --clean \
    --distpath="." \
    --name="Windown-JW-File-Merge" \
    --icon="extra/icon.png" \
    main.py