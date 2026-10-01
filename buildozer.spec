[app]
title = Media Downloader
package.name = mediadownloader
package.domain = org.ormanzhisv
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ico
version = 1.0.0

# Зависимости, необходимые для работы Kivy и загрузки медиа
requirements = python3,kivy==2.3.0,requests,yt-dlp,urllib3,certifi,idna,jnius,android


orientation = portrait
fullscreen = 0
icon.filename = icon.ico

[buildozer]
log_level = 2
warn_on_root = 0

[android]
# Указываем Buildozer брать уже готовый SDK и NDK от GitHub Actions
android.sdk = /usr/local/lib/android/sdk
android.ndk = /usr/local/lib/android/sdk/ndk-bundle

# Архитектуры процессоров для сборки
android.archs = armeabi-v7a, arm64-v8a

# Минимальная и целевая версии Android SDK
android.api = 33
android.minapi = 21

# Разрешения на чтение/запись файлов и доступ в интернет
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
source.exclude_patterns = app.py,create_installer.bat,test_mobile.py,verify_mobile.py

# Имя главного файла для мобильной версии (у автора это main.py)
android.entrypoint = main.py
