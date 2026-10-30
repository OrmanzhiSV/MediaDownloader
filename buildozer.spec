[app]
title = Media Downloader
package.name = mediadownloader
package.domain = org.ormanzhisv
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ico
version = 1.0.0

# Чистые мобильные требования. Модули jnius и android Kivy соберет сам локально внутри контейнера!
requirements = python3,kivy==2.3.0,requests,yt-dlp,urllib3,certifi,idna

orientation = portrait
fullscreen = 0
icon.filename = icon.ico

# Указываем целевую версию Android (API 36 для Android 16)
android.api = 36
# Минимальная версия, которую поддерживаем (можно оставить 21 или 24)
android.minapi = 24
# Используем современный NDK (r27+ обязателен для новых Android)
android.ndk = 27b
# Ветка p4a, которая содержит исправления для новых Android
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 0

[android]
android.accept_sdk_license = True

# Архитектуры процессоров для сборки
android.archs = armeabi-v7a, arm64-v8a

# Актуальные и доступные в контейнере версии SDK
android.api = 33
android.minapi = 21

# Системные разрешения для работы загрузчика на телефоне
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
source.exclude_patterns = app.py,create_installer.bat,test_mobile.py,verify_mobile.py

# Имя главного файла мобильной версии
android.entrypoint = main.py
