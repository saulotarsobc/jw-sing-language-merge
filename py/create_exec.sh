#! bash
pyinstaller \
    -F \
    --name "Windown-JW-File-Merge" \
    --specpath ./extra \
    --distpath "./" \
    -i "./icon.png" \
    -c ./src/main.py