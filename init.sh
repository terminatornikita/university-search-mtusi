#!/bin/bash
# Загрузка тестовых документов через API
echo "Загрузка тестовых документов..."
for f in test_lectures/*.docx; do
    if [ -f "$f" ]; then
        echo "Загрузка: $f"
        curl -X POST -F "file=@$f" http://localhost:8000/api/v1/documents/upload || true
    fi
done
echo "Готово!"
