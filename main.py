import os
import sys
import traceback
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
import yt_dlp
import threading


class MediaDownloaderApp(App):
    def build(self):
        self.title = "Media Downloader"
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(
            text="Введите ссылку для скачивания:",
            size_hint_y=None, height=30
        ))
        
        self.url_input = TextInput(
            multiline=False,
            hint_text="https://youtube.com...",
            size_hint_y=None, height=50
        )
        layout.add_widget(self.url_input)
        
        self.status_label = Label(
            text="Статус: Ожидание",
            size_hint_y=None, height=30
        )
        layout.add_widget(self.status_label)
        
        download_btn = Button(
            text="Скачать Видео (480p)",
            size_hint_y=None, height=50,
            background_color=(0, 0.6, 0.8, 1)
        )
        download_btn.bind(on_press=self.start_download)
        layout.add_widget(download_btn)
        
        return layout

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
            Clock.schedule_once(lambda dt: self.update_status("Успешно скачано!"), 0)
        except Exception as e:
            Clock.schedule_once(
                lambda dt: self.update_status(f"Ошибка: {str(e)[:50]}"), 0
            )

    def update_status(self, text):
        self.status_label.text = text


if __name__ == '__main__':
    try:
        MediaDownloaderApp().run()
    except Exception:
        with open('/sdcard/Download/crash_log.txt', 'w') as f:
            f.write(traceback.format_exc())
        sys.exit(1)
