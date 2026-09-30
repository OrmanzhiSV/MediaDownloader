import os
import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.progressbar import Progressbar
from kivy.clock import Clock
import yt_dlp

class MediaDownloaderApp(App):
    def build(self):
        self.title = "Media Downloader"
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text="Введите ссылку для скачивания:", size_hint_y=None, height=30))
        
        self.url_input = TextInput(multiline=False, hint_text="https://youtube.com... ", size_hint_y=None, height=50)
        layout.add_widget(self.url_input)
        
        self.status_label = Label(text="Статус: Ожидание", size_hint_y=None, height=30)
        layout.add_widget(self.status_label)
        
        download_btn = Button(text="Скачать Видео (480p)", size_hint_y=None, height=50, background_color=(0, 0.6, 0.8, 1))
        download_btn.bind(on_press=self.start_download)
        layout.add_widget(download_btn)
        
        return layout

    def start_download(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = "Статус: Ссылка пустая!"
            return
        
        self.status_label.text = "Статус: Скачивание началось..."
        # Запуск скачивания в отдельном потоке, чтобы интерфейс не зависал
        import threading
        threading.Thread(target=self.download_logic, args=(url,)).start()

    def download_logic(self, url):
        # Определение пути сохранения на Android устройствах (папка Downloads)
        try:
            from android.storage import primary_external_storage_path
            download_dir = os.path.join(primary_external_storage_path(), "Download")
        except ImportError:
            download_dir = os.path.expanduser("~/Downloads")

        ydl_opts = {
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            'nocheckcertificate': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            Clock.schedule_once(lambda dt: self.update_status("Успешно скачано в Downloads!"), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_status(f"Ошибка: {str(e)[:30]}"), 0)

    def update_status(self, text):
        self.status_label.text = text

if __name__ == '__main__':
    MediaDownloaderApp().run()
