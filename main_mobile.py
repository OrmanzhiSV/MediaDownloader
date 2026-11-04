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
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window

# Устанавливаем светлый фон
Window.clearcolor = (0.95, 0.95, 0.95, 1)

# Защита от конфликта логгеров Kivy и yt-dlp
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except Exception as e:
    YT_DLP_AVAILABLE = False
    YT_DLP_ERROR = str(e)


class EmptyLogger:
    """Пустой логгер, чтобы yt-dlp не писал в stdout и не ломал Kivy"""
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


class MediaDownloaderApp(App):
    def build(self):
        self.title = 'Media Downloader'
        
        if not YT_DLP_AVAILABLE:
            layout = BoxLayout(orientation='vertical', padding=20)
            layout.add_widget(Label(
                text=f"Критическая ошибка:\nМодуль yt-dlp не загружен.\n{YT_DLP_ERROR}",
                color=(1, 0, 0, 1),
                halign='center'
            ))
            return layout

        tab_panel = TabbedPanel(do_default_tab=False)
        
        download_tab = TabbedPanelItem(text='Download')
        download_tab.add_widget(self.create_download_layout())
        tab_panel.add_widget(download_tab)
        
        settings_tab = TabbedPanelItem(text='Settings')
        settings_tab.add_widget(self.create_settings_layout())
        tab_panel.add_widget(settings_tab)
        
        return tab_panel
    
    def create_download_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Статус
        self.status_label = Label(
            text='Готов к работе', 
            size_hint_y=None, height=40,
            color=(0, 0, 0, 1)
        )
        layout.add_widget(self.status_label)
        
        # Ввод URL + Вставить
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
        self.url_input = TextInput(
            multiline=False, hint_text='Вставьте ссылку...',
            background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1),
        )
        paste_btn = Button(text='Вставить', size_hint_x=0.3, background_color=(0.5, 0.5, 0.8, 1))
        paste_btn.bind(on_press=self.paste_url)
        input_layout.add_widget(self.url_input)
        input_layout.add_widget(paste_btn)
        layout.add_widget(input_layout)
        
        # --- БЛОК: Выбор формата ---
        format_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        format_layout.add_widget(Label(text="Формат:", color=(0,0,0,1), size_hint_x=0.3))
        self.format_btn = Button(text='480p', size_hint_x=0.7)
        self.selected_format = '480p'
        self.format_dropdown = DropDown()
        for text, value in [('360p', '360p'), ('480p', '480p'), ('Аудио', 'audio')]:
            btn = Button(text=text, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn, val=value, txt=text: self.select_format(val, txt))
            self.format_dropdown.add_widget(btn)
        self.format_btn.bind(on_release=self.format_dropdown.open)
        self.format_dropdown.bind(on_select=lambda instance, x: setattr(self.format_btn, 'text', x))
        format_layout.add_widget(self.format_btn)
        layout.add_widget(format_layout)

        # --- БЛОК: Выбор языка ---
        lang_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        lang_layout.add_widget(Label(text="Язык аудио:", color=(0,0,0,1), size_hint_x=0.3))
        self.lang_btn = Button(text='Оригинал', size_hint_x=0.7)
        self.selected_lang = ''
        self.lang_dropdown = DropDown()
        for text, value in [('Оригинал', ''), ('Украинский', 'uk'), ('Русский', 'ru')]:
            btn = Button(text=text, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn, val=value, txt=text: self.select_lang(val, txt))
            self.lang_dropdown.add_widget(btn)
        self.lang_btn.bind(on_release=self.lang_dropdown.open)
        self.lang_dropdown.bind(on_select=lambda instance, x: setattr(self.lang_btn, 'text', x))
        lang_layout.add_widget(self.lang_btn)
        layout.add_widget(lang_layout)
        
        # Кнопка скачивания
        self.download_btn = Button(
            text='Скачать', size_hint_y=None, height=60,
            background_color=(0.1, 0.7, 0.3, 1), color=(1, 1, 1, 1)
        )
        self.download_btn.bind(on_press=self.start_download)
        layout.add_widget(self.download_btn)
        
        # Прогресс-бар
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=30)
        layout.add_widget(self.progress_bar)
        
        return layout
    
    def create_settings_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(Label(text='Настройки', color=(0,0,0,1), font_size='20sp', size_hint_y=None, height=40))
        layout.add_widget(Label(text='Выбор формата и языка\ndоступен на главном экране.', color=(0.3,0.3,0.3,1)))
        return layout

    def select_format(self, value, text):
        self.selected_format = value
        self.format_dropdown.select(text)

    def select_lang(self, value, text):
        self.selected_lang = value
        self.lang_dropdown.select(text)

    def paste_url(self, instance):
        try:
            self.url_input.text = Clipboard.paste()
        except Exception:
            self.status_label.text = "Ошибка: буфер обмена пуст"

    def start_download(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = 'Ошибка: Введите ссылку!'
            return
        
        self.download_btn.disabled = True
        self.progress_bar.value = 0
        self.status_label.text = 'Подготовка...'
        
        threading.Thread(target=self.download_worker, args=(url,), daemon=True).start()
    
    def download_worker(self, url):
        try:
            # 1. Папка для скачивания
            try:
                from android.storage import app_storage_path
                download_dir = os.path.join(app_storage_path(), "Download")
                os.makedirs(download_dir, exist_ok=True)
            except Exception as e:
                err = str(e)
                Clock.schedule_once(lambda dt, m=err: setattr(self.status_label, 'text', f'Ошибка папки: {m}'), 0)
                return

            # 2. Формируем строку формата (как в вашем Windows-приложении, но с фоллбеками)
            lang_filter = f"[language^={self.selected_lang}]" if self.selected_lang else ""
            
            if self.selected_format == 'audio':
                format_string = f"bestaudio{lang_filter}/bestaudio/best"
            else:
                height = 480 if self.selected_format == '480p' else 360
                # Пытаемся взять mp4/avc + m4a на нужном языке, если нет — любое видео + аудио, если нет — готовый файл
                format_string = (
                    f"bestvideo[height<={height}][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]{lang_filter}/"
                    f"bestvideo[height<={height}]+bestaudio{lang_filter}/"
                    f"best[height<={height}]/"
                    f"best"
                )

            ydl_opts = {
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'format': format_string,
                'nocheckcertificate': True,
                'quiet': True,
                'no_warnings': True,
                'noprogress': True,
                'logger': EmptyLogger(),
                'cachedir': os.path.join(app_storage_path(), '.cache'),
            }
            
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'Скачивание...'), 0)
            
            # 3. Запуск
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # 4. Успех
            Clock.schedule_once(lambda dt: self.on_success(), 0)
            
        except Exception as e:
            err_msg = str(e)[:100]
            Clock.schedule_once(lambda dt, msg=err_msg: self.on_error(msg), 0)
            
    def on_success(self):
        self.status_label.text = 'Успешно скачано!'
        self.progress_bar.value = 100
        self.download_btn.disabled = False
        
    def on_error(self, message):
        self.status_label.text = f'Ошибка: {message}'
        self.download_btn.disabled = False


if __name__ == '__main__':
    try:
        MediaDownloaderApp().run()
    except Exception:
        try:
            from android.storage import app_storage_path
            log_path = os.path.join(app_storage_path(), "crash_log.txt")
        except:
            log_path = "crash_log.txt"
        with open(log_path, 'w') as f:
            f.write(traceback.format_exc())
        sys.exit(1)
