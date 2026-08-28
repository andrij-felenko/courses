#!/usr/bin/env bash
set -e

deploy_service() {
    echo "Початок розгортання..."
    cp /non/existent/config.json /etc/app/config.json  # Помилка: файл не існує!
    echo "Конфігурацію скопійовано."
    systemctl restart my_app
}

# Виклик функції всередині умови if:
if deploy_service; then
    echo "Розгортання пройшло успішно!"
else
    echo "Збій розгортання!"
fi
