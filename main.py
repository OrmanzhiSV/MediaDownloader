import os
import sys
import traceback
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
import yt_dlp

# Светлый фон вместо черного
Window.clearcolor = (0.95, 0.95, 0.95, 1)


class MediaDownloaderApp(App):
    def build(self):
        self.title = "Media Downloader"
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        layout.add_widget(Label(
            text="Введите ссылку для скачивания:",
            size_hint_y=None, height=40,
            color=(0, 0, 0, 1)
        ))
        
        # Поле ввода + кнопка вставки
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.url_input = TextInput(
            multiline=False,
            hint_text="https://youtube.com...",
            size_hint_x=0.8
        )
        input_layout.add_widget(self.url_input)
        
        paste_btn = Button(
            text="Вставить",
            size_hint_x=0.2,
            background_color=(0.4, 0.6, 0.8, 1)
        )
        paste_btn.bind(on_press=self.paste_url)
        input_layout.add_widget(paste_btn)
        
        layout.add_widget(input_layout)
        
        self.status_label = Label(
            text="Статус: Ожидание",
            size_hint_y=None, height=40,
            color=(0, 0, 0, 1)
        )
        layout.add_widget(self.status_label)
        
        download_btn = Button(
            text="Скачать Видео (480p)",
            size_hint_y=None, height=60,
            background_color=(0.2, 0.7, 0.3, 1)
        )
        download_btn.bind(on_press=self.start_download)
        layout.add_widget(download_btn)
        
        return layout

    def paste_url(self, instance):
        try:
            self.url_input.text = Clipboard.paste()
        except Exception:
            self.status_label.text = "Ошибка: буфер обмена пуст"

    def start_download(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = "Статус: Ссылка пустая!"
            return
        
        self.status_label.text = "Статус: Скачивание началось..."
        threading.Thread(target=self.download_logic, args=(url,), daemon=True).start()

    def download_logic(self, url):
        try:
            from android.storage import app_storage_path
            download_dir = os.path.join(app_storage_path(), "Download")
            os.makedirs(download_dir, exist_ok=True)
        except ImportError:
            download_dir = os.path.expanduser("~/Downloads")
            os.makedirs(download_dir, exist_ok=True)

        ydl_opts = {
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            'nocheckcertificate': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            # ИСПРАВЛЕНИЕ: передаем сообщение через аргумент по умолчанию
            Clock.schedule_once(lambda dt: self.update_status("Успешно скачано!"), 0)
        except Exception as e:
            # ИСПРАВЛЕНИЕ: фиксируем строку ошибки ДО создания lambda
            err_msg = str(e)[:50]
            Clock.schedule_once(lambda dt, msg=err_msg: self.update_status(f"Ошибка: {msg}"), 0)

    def update_status(self, text):
        self.status_label.text = text


if __name__ == '__main__':
    try:
        MediaDownloaderApp().run()
    except Exception:
        # Лог пишем в приватную папку приложения, так как /sdcard/Download/ на новых Android закрыт
        try:
            from android.storage import app_storage_path
            log_path = os.path.join(app_storage_path(), "crash_log.txt")
        except ImportError:
            log_path = "crash_log.txt"
            
        with open(log_path, 'w') as f:
            f.write(traceback.format_exc())
        sys.exit(1)
