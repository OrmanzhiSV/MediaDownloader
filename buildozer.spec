[app]
title = Media Downloader
package.name = mediadownloader
package.domain = org.ormanzhisv
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ico
version = 1.0.0

# Зависимости, необходимые для работы Kivy и загрузки медиа
requirements = python3,kivy==2.3.0,requests,yt-dlp,urllib3,certifi,idna,jnius

orientation = portrait
fullscreen = 0
icon.filename = icon.ico

[buildozer]
log_level = 2
warn_on_root = 0

[android]
# Архитектуры процессоров для сборки
android.archs = armeabi-v7a, arm64-v8a

# Минимальная и целевая версии Android SDK
android.api = 33
android.minapi = 21

# Разрешения на чтение/запись файлов и доступ в интернет
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# Имя главного файла для мобильной версии (у автора это main_mobile.py)
android.entrypoint = main_mobile.py
