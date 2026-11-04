[app]
title = Media Downloader
package.name = mediadownloader
package.domain = org.ormanzhisv
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ico
version = 1.0.0

# Требования (kivy 2.3.0 совместим с Python 3.11)
requirements = python3,kivy==2.3.0,requests,yt-dlp,urllib3,certifi,idna,pyjnius

orientation = portrait
fullscreen = 0
icon.filename = icon.ico

# --- Android настройки (только один раз!) ---
android.api = 36
android.minapi = 24
android.ndk = 25c
p4a.branch = develop

# Разрешения: только INTERNET (для yt-dlp). 
# Запись в Download через Scoped Storage не работает без специальных API.
android.permissions = INTERNET

# Исключаем лишние файлы из сборки
source.exclude_patterns = app.py,create_installer.bat,test_mobile.py,verify_mobile.py

# Добавляем Gradle-зависимости для FFmpeg-Kit
android.gradle_dependencies = com.arqies:ffmpeg-kit-python:6.0-2.LTS@aar, com.arthenica:smart-exception-common:0.2.1@jar, com.arthenica:smart-exception-java:0.2.1@jar

# Добавляем репозиторий, откуда качать библиотеку
android.add_gradle_repositories = maven {url 'https://Arqies-Repositories.github.io/Gradle-FFmpeg-Kit-Python/'}

# Включаем AndroidX (требуется для библиотеки)
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 0
