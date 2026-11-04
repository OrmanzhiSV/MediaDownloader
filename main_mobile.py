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

# Импортируем pyjnius для вызова FFmpeg
from jnius import autoclass

# Устанавливаем светлый фон
Window.clearcolor = (0.95, 0.95, 0.95, 1)

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except Exception as e:
    YT_DLP_AVAILABLE = False
    YT_DLP_ERROR = str(e)


class EmptyLogger:
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
        
        self.status_label = Label(
            text='Готов к работе', size_hint_y=None, height=40,
            color=(0, 0, 0, 1)
        )
        layout.add_widget(self.status_label)
        
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
        
        # Выбор формата
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

        # Выбор языка
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
        
        self.download_btn = Button(
            text='Скачать', size_hint_y=None, height=60,
            background_color=(0.1, 0.7, 0.3, 1), color=(1, 1, 1, 1)
        )
        self.download_btn.bind(on_press=self.start_download)
        layout.add_widget(self.download_btn)
        
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=30)
        layout.add_widget(self.progress_bar)
        
        return layout
    
    def create_settings_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(Label(text='Настройки', color=(0,0,0,1), font_size='20sp', size_hint_y=None, height=40))
        layout.add_widget(Label(text='Выбор формата и языка\nдоступен на главном экране.', color=(0.3,0.3,0.3,1)))
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
            from android.storage import app_storage_path
            download_dir = os.path.join(app_storage_path(), "Download")
            os.makedirs(download_dir, exist_ok=True)

            # 2. Формируем строку формата (раздельные видео и аудио)
            lang_filter = f"[language^={self.selected_lang}]" if self.selected_lang else ""
            
            if self.selected_format == 'audio':
                format_string = f"bestaudio{lang_filter}/bestaudio"
            else:
                height = 480 if self.selected_format == '480p' else 360
                format_string = (
                    f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]{lang_filter}/"
                    f"bestvideo[height<={height}]+bestaudio{lang_filter}"
                )

            ydl_opts = {
                'outtmpl': os.path.join(download_dir, '%(title)s.f%(format_id)s.%(ext)s'),
                'format': format_string,
                'nocheckcertificate': True,
                'quiet': True,
                'no_warnings': True,
                'noprogress': True,
                'logger': EmptyLogger(),
                'cachedir': os.path.join(app_storage_path(), '.cache'),
                # КРИТИЧЕСКИ ВАЖНО: говорим yt-dlp НЕ искать ffmpeg и не пытаться склеивать
                'ffmpeg_location': None, 
                'postprocessors': [], # Убираем автоматические постпроцессоры
            }
            
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'Скачивание потоков...'), 0)
            
            # 3. Скачиваем БЕЗ склейки
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                requested_downloads = info.get('requested_downloads', [])
                if not requested_downloads:
                    raise Exception("Не удалось получить информацию о скачанных файлах")
                
                filepaths = [dl['filepath'] for dl in requested_downloads]
                
                if len(filepaths) < 2:
                    # Если скачался только один файл (например, аудио), просто оставляем его
                    final_path = filepaths[0]
                else:
                    # 4. Склеиваем через FFmpeg-Kit
                    Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'Склейка...'), 0)
                    
                    video_path = None
                    audio_path = None
                    for p in filepaths:
                        if '.m4a' in p or '.webm' in p or 'audio' in p.lower():
                            audio_path = p
                        else:
                            video_path = p
                    
                    if not video_path or not audio_path:
                        # Если не удалось определить, пробуем взять первые два
                        video_path, audio_path = filepaths[0], filepaths[1]

                    final_path = os.path.join(download_dir, f"{info['title']}.mp4")
                    
                    # Вызываем FFmpeg через pyjnius
                    from jnius import autoclass
                    FFMPEG = autoclass('com.sahib.pyff.ffpy')
                    
                    # Команда для склейки
                    cmd = f'-i "{video_path}" -i "{audio_path}" -c copy "{final_path}"'
                    output = FFMPEG.Run(cmd)
                    
                    # Удаляем временные файлы
                    try:
                        os.remove(video_path)
                        os.remove(audio_path)
                    except:
                        pass

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
