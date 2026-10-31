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
from kivy.core.window import Window

# Делаем фон белым, чтобы избежать "черного экрана"
Window.clearcolor = (0.95, 0.95, 0.95, 1)

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except Exception as e:
    YT_DLP_AVAILABLE = False
    YT_DLP_ERROR = str(e)


class MediaDownloaderApp(App):
    def build(self):
        self.title = 'Media Downloader'
        
        # Если yt_dlp не загрузился, показываем ошибку на экране
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
        settings_tab.add_widget(Label(text='Settings here', color=(0,0,0,1)))
        tab_panel.add_widget(settings_tab)
        
        return tab_panel
    
    def create_download_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        self.status_label = Label(
            text='Готов к работе', 
            size_hint_y=None, height=40,
            color=(0, 0, 0, 1)
        )
        layout.add_widget(self.status_label)
        
        # Поле ввода + кнопка вставки
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
        self.url_input = TextInput(
            multiline=False,
            hint_text='Вставьте ссылку...',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
        )
        paste_btn = Button(text='Вставить', size_hint_x=0.3, background_color=(0.5, 0.5, 0.8, 1))
        paste_btn.bind(on_press=self.paste_url)
        input_layout.add_widget(self.url_input)
        input_layout.add_widget(paste_btn)
        layout.add_widget(input_layout)
        
        # Кнопка скачивания
        self.download_btn = Button(
            text='Скачать Видео (480p)', 
            size_hint_y=None, height=60,
            background_color=(0.1, 0.7, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        self.download_btn.bind(on_press=self.start_download)
        layout.add_widget(self.download_btn)
        
        # Прогресс-бар
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=30)
        layout.add_widget(self.progress_bar)
        
        return layout
    
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
        self.status_label.text = 'Скачивание началось...'
        
        threading.Thread(target=self.download_worker, args=(url,), daemon=True).start()
    
    def download_worker(self, url):
        try:
            # 1. Создаем папку для скачивания
            # Используем app_storage_path() — это приватная папка приложения, куда писать можно без разрешений
            try:
                from android.storage import app_storage_path
                download_dir = os.path.join(app_storage_path(), "Download")
                os.makedirs(download_dir, exist_ok=True)
                # Проверяем, что папка действительно создалась и в нее можно писать
                test_file = os.path.join(download_dir, "test.txt")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'Папка готова. Начинаем...'), 0)
            except Exception as e:
                err = str(e)
                Clock.schedule_once(lambda dt, m=err: setattr(self.status_label, 'text', f'Ошибка папки: {m}'), 0)
                return

            # 2. Настраиваем yt-dlp
            ydl_opts = {
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'format': 'best[height<=480]/best',
                'nocheckcertificate': True,
                'quiet': True,          # Отключаем лишний вывод в консоль
                'no_warnings': True,    # Отключаем предупреждения
                'noprogress': True,     # Отключаем прогресс-бар yt-dlp (у нас свой)
                # Явно указываем, куда писать кэш (в приватную папку)
                'cachedir': os.path.join(app_storage_path(), '.cache'),
            }
            
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'Скачивание...'), 0)
            
            # 3. Запускаем скачивание
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
        # Сохраняем лог
        try:
            from android.storage import app_storage_path
            log_path = os.path.join(app_storage_path(), "crash_log.txt")
        except:
            log_path = "crash_log.txt"
        with open(log_path, 'w') as f:
            f.write(traceback.format_exc())
        sys.exit(1)
