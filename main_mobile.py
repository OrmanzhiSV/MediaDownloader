import os
import sys
import traceback
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
import yt_dlp


class MediaDownloaderApp(App):
    def build(self):
        self.title = 'Media Downloader'
        
        tab_panel = TabbedPanel(do_default_tab=False)
        
        download_tab = TabbedPanelItem(text='Download')
        download_tab.add_widget(self.create_download_layout())
        tab_panel.add_widget(download_tab)
        
        settings_tab = TabbedPanelItem(text='Settings')
        settings_tab.add_widget(self.create_settings_layout())
        tab_panel.add_widget(settings_tab)
        
        history_tab = TabbedPanelItem(text='History')
        history_tab.add_widget(self.create_history_layout())
        tab_panel.add_widget(history_tab)
        
        return tab_panel
    
    def create_download_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        title_label = Label(
            text='Media Downloader', 
            size_hint_y=None, height=40,
            color=(0.2, 0.6, 1, 1),
            font_size='20sp', bold=True
        )
        layout.add_widget(title_label)
        
        url_label = Label(
            text='Enter Media URLs:', 
            size_hint_y=None, height=30,
            color=(0.3, 0.3, 0.3, 1),
            font_size='16sp'
        )
        layout.add_widget(url_label)
        
        # Поле ввода + кнопка вставки
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        self.url_input = TextInput(
            multiline=False,
            hint_text='Paste your media link here...',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
        )
        paste_btn = Button(text='Вставить', size_hint_x=0.3, background_color=(0.5, 0.5, 0.8, 1))
        paste_btn.bind(on_press=self.paste_url)
        input_layout.add_widget(self.url_input)
        input_layout.add_widget(paste_btn)
        layout.add_widget(input_layout)
        
        button_layout = BoxLayout(size_hint_y=None, height=60, spacing=15)
        self.video_button = Button(
            text='Download Video', 
            background_color=(0.1, 0.7, 0.3, 1),
            color=(1, 1, 1, 1), bold=True, font_size='16sp'
        )
        self.video_button.bind(on_press=self.on_video_button_press)
        
        self.audio_button = Button(
            text='Download Audio', 
            background_color=(0.2, 0.5, 0.9, 1),
            color=(1, 1, 1, 1), bold=True, font_size='16sp'
        )
        self.audio_button.bind(on_press=self.on_audio_button_press)
        
        button_layout.add_widget(self.video_button)
        button_layout.add_widget(self.audio_button)
        layout.add_widget(button_layout)
        
        self.progress_bar = ProgressBar(
            max=100, value=0, size_hint_y=None, height=35,
            color=(0.2, 0.7, 0.9, 1)
        )
        layout.add_widget(self.progress_bar)
        
        self.status_label = Label(
            text='Ready to download your media files.',
            color=(0.2, 0.2, 0.2, 1), font_size='15sp'
        )
        layout.add_widget(self.status_label)
        
        return layout
    
    def paste_url(self, instance):
        try:
            self.url_input.text = Clipboard.paste()
        except Exception:
            self.status_label.text = "Ошибка: буфер обмена пуст"
    
    def create_settings_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        title_label = Label(
            text='Settings', size_hint_y=None, height=40,
            color=(0.2, 0.6, 1, 1), font_size='20sp', bold=True
        )
        layout.add_widget(title_label)
        layout.add_widget(Label(
            text='Settings will be available in the full implementation.',
            color=(0.3, 0.3, 0.3, 1)
        ))
        return layout
    
    def create_history_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        title_label = Label(
            text='Download History', size_hint_y=None, height=40,
            color=(0.2, 0.6, 1, 1), font_size='20sp', bold=True
        )
        layout.add_widget(title_label)
        layout.add_widget(Label(
            text='Your download history will appear here.',
            color=(0.3, 0.3, 0.3, 1)
        ))
        return layout
    
    def on_video_button_press(self, instance):
        self.start_download('video')
    
    def on_audio_button_press(self, instance):
        self.start_download('audio')
    
    def start_download(self, download_type):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = 'Please enter a URL.'
            self.status_label.color = (0.9, 0.2, 0.2, 1)
            return
        
        self.video_button.disabled = True
        self.audio_button.disabled = True
        self.url_input.disabled = True
        
        self.progress_bar.value = 0
        self.status_label.text = f'Starting {download_type} download...'
        self.status_label.color = (0.2, 0.2, 0.2, 1)
        
        threading.Thread(target=self.download_worker, args=(url, download_type), daemon=True).start()
    
    def download_worker(self, url, download_type):
        try:
            from android.storage import app_storage_path
            download_dir = os.path.join(app_storage_path(), "Download")
            os.makedirs(download_dir, exist_ok=True)
        except ImportError:
            download_dir = os.path.expanduser("~/Downloads")
            os.makedirs(download_dir, exist_ok=True)
        
        # Настройка формата
        if download_type == 'audio':
            ydl_opts = {
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'format': 'bestaudio/best',
                'nocheckcertificate': True,
                'progress_hooks': [self.progress_hook],
            }
        else:
            ydl_opts = {
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
                'nocheckcertificate': True,
                'progress_hooks': [self.progress_hook],
            }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            Clock.schedule_once(lambda dt: self.download_complete(), 0)
        except Exception as e:
            err_msg = str(e)  # ФИКСИРУЕМ ОШИБКУ ДО LAMBDA
            Clock.schedule_once(lambda dt, msg=err_msg: self.download_error(msg), 0)
    
    def progress_hook(self, d):
        """Вызывается yt-dlp при обновлении прогресса"""
        if d['status'] == 'downloading':
            # Вычисляем процент
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percent = (downloaded / total) * 100
                # Обновляем UI в основном потоке
                Clock.schedule_once(lambda dt, p=percent: setattr(self.progress_bar, 'value', p), 0)
        elif d['status'] == 'finished':
            Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 100), 0)
    
    def download_complete(self):
        self.status_label.text = 'Скачивание завершено успешно!'
        self.status_label.color = (0.1, 0.7, 0.3, 1)
        self.progress_bar.value = 100
        self.video_button.disabled = False
        self.audio_button.disabled = False
        self.url_input.disabled = False
    
    def download_error(self, error):
        self.status_label.text = f'Ошибка: {error[:50]}'
        self.status_label.color = (0.9, 0.2, 0.2, 1)
        self.video_button.disabled = False
        self.audio_button.disabled = False
        self.url_input.disabled = False


if __name__ == '__main__':
    try:
        MediaDownloaderApp().run()
    except Exception:
        try:
            from android.storage import app_storage_path
            log_path = os.path.join(app_storage_path(), "crash_log.txt")
        except ImportError:
            log_path = "crash_log.txt"
        with open(log_path, 'w') as f:
            f.write(traceback.format_exc())
        sys.exit(1)
