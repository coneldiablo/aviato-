import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QSpinBox, QTextEdit, QFileDialog)
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from nmap_scanner import NmapScanner
import threading
import time

class MainWindow(QMainWindow):
    # Создаем сигнал для обновления текстового поля и прогресса
    text_update_signal = pyqtSignal(str)
    progress_update_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nmap CI/CD Integration")
        self.setGeometry(100, 100, 800, 600)
        self.is_scanning = False
        self.initUI()

        # Подключаем сигнал к слоту для обновления текстового поля
        self.text_update_signal.connect(self.update_text_output)
        self.progress_update_signal.connect(self.update_progress)

    def initUI(self):
        # Подключаем шрифт Soyuz Grotesk
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Soyuz Grotesk Regular.ttf')
        QFontDatabase.addApplicationFont(font_path)
        font = QFont("Soyuz Grotesk", 12)

        # Поле для вывода результатов
        self.result_output = QTextEdit()
        self.result_output.setFont(font)
        self.result_output.setReadOnly(True)

        # Поле для ввода URL
        url_label = QLabel("Тестируемый URL/IP:")
        url_label.setFont(font)
        self.url_input = QLineEdit()
        self.url_input.setFont(font)

        # Кнопка очистки URL
        clear_url_button = QPushButton("Очистить")
        clear_url_button.setFont(font)
        clear_url_button.clicked.connect(self.clear_url)

        # Поле для ввода интервала
        interval_label = QLabel("Интервал (мин):")
        interval_label.setFont(font)
        self.interval_input = QSpinBox()
        self.interval_input.setFont(font)
        self.interval_input.setMinimum(1)
        self.interval_input.setMaximum(1440)

        # Кнопка запуска
        self.start_button = QPushButton("Старт")
        self.start_button.setFont(font)
        self.start_button.clicked.connect(self.start_scan)

        # Кнопка остановки
        self.stop_button = QPushButton("Стоп")
        self.stop_button.setFont(font)
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)

        # Поле для отображения прогресса
        self.progress_label = QLabel("Прогресс: 0%")
        self.progress_label.setFont(font)

        # Размещение элементов интерфейса
        main_layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        interval_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        input_layout.addWidget(url_label)
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(clear_url_button)

        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_input)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        main_layout.addLayout(input_layout)
        main_layout.addLayout(interval_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.result_output)
        main_layout.addWidget(self.progress_label)

        # Устанавливаем центральный виджет
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    # Слот для обновления текстового поля
    def update_text_output(self, text):
        self.result_output.append(text)

    # Слот для обновления прогресса
    def update_progress(self, progress):
        self.progress_label.setText(f"Прогресс: {progress}%")

    def clear_url(self):
        self.url_input.clear()

    def start_scan(self):
        if self.is_scanning:
            self.text_update_signal.emit("Пентест уже запущен.")
            return

        # Получаем URL или используем "localhost", если поле пустое
        url = self.url_input.text().strip()
        interval = self.interval_input.value()

        # Если URL не указан, по умолчанию использовать "localhost"
        if not url:
            url = "localhost"
            self.text_update_signal.emit(f"Сканирование по умолчанию запущено для {url}.")
        elif url.lower() == "localhost":
            self.text_update_signal.emit(f"Сканирование запущено для локального сайта {url}.")
        else:
            self.text_update_signal.emit(f"Начинается сканирование для {url} с интервалом {interval} минут.")

        self.is_scanning = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # Запуск в отдельном потоке
        self.scan_thread = threading.Thread(target=self.run_scan, args=(url, interval), daemon=True)
        self.scan_thread.start()

    def stop_scan(self):
        if self.is_scanning:
            self.text_update_signal.emit("Остановка пентеста...")
            self.is_scanning = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
        else:
            self.text_update_signal.emit("Пентест не запущен.")

    def run_scan(self, url, interval):
        scanner = NmapScanner()
        try:
            # Отображаем прогресс
            self.text_update_signal.emit(f"Запуск Nmap для {url}...")
            self.progress_update_signal.emit(10)  # Инициализация, 10%

            # Этап 1: Сканирование хоста
            time.sleep(2)  # Имитация времени на этап
            self.text_update_signal.emit(f"Этап 1: Сканирование хоста для {url}...")
            self.progress_update_signal.emit(30)  # 30% прогресса

            # Этап 2: Сканирование портов
            report = scanner.run_scan(url)
            self.text_update_signal.emit(f"Этап 2: Сканирование портов для {url}...")
            self.progress_update_signal.emit(60)  # 60% прогресса

            # Этап 3: Завершение и анализ сервисов
            time.sleep(2)  # Имитация времени на этап
            self.text_update_signal.emit(f"Этап 3: Завершение сканирования для {url}...")
            self.progress_update_signal.emit(90)  # 90% прогресса

            # Выводим отчет
            self.text_update_signal.emit(f"Отчет:\n{report}")
            self.progress_update_signal.emit(100)  # Завершение, 100%

            # Сохранение отчета после завершения пентеста
            self.save_report(report)

        except Exception as e:
            self.text_update_signal.emit(f"Ошибка при запуске сканирования: {e}")
            self.is_scanning = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            return

        self.text_update_signal.emit("Отчет отправлен по электронной почте.")
        self.is_scanning = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    # Диалоговое окно для сохранения отчета
    def save_report(self, report):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", "", "Text Files (*.txt);;All Files (*)", options=options)
        
        if file_path:
            with open(file_path, 'w') as file:
                file.write(report)
            self.text_update_signal.emit(f"Отчет сохранен в: {file_path}")
        else:
            self.text_update_signal.emit("Сохранение отчета отменено.")
