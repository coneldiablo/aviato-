import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QSpinBox, QTextEdit, QFileDialog, QMessageBox)
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from nmap_scanner import NmapScanner
import socket

# Класс для выполнения Nmap сканирования в отдельном потоке
class ScanWorker(QThread):
    # Сигналы для передачи данных в основной поток
    progress_signal = pyqtSignal(int)
    text_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)

    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self._is_running = True  # Флаг для остановки сканирования

    def run(self):
        try:
            scanner = NmapScanner()
            self.text_signal.emit(f"Запуск Nmap для {self.domain}...")
            self.progress_signal.emit(10)

            # Выполняем полное сканирование с поиском уязвимостей
            report = scanner.run_scan(self.domain)

            if report is None:
                self.text_signal.emit("Сканирование завершено, но хосты не найдены.")
                self.finished_signal.emit("")
                return

            if not self._is_running:  # Прерывание потока, если пентест остановлен
                self.text_signal.emit("Пентест остановлен.")
                self.finished_signal.emit("")
                return

            self.text_signal.emit("Сканирование завершено.")
            self.progress_signal.emit(100)
            self.finished_signal.emit(report)

        except Exception as e:
            self.text_signal.emit(f"Ошибка при запуске сканирования: {e}")
            self.finished_signal.emit("")

    def stop(self):
        self._is_running = False  # Прерывание сканирования

class MainWindow(QMainWindow):
    # Сигналы для обновления текстового поля и прогресса
    text_update_signal = pyqtSignal(str)
    progress_update_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nmap CI/CD Integration")
        self.setGeometry(100, 100, 800, 600)
        self.is_scanning = False
        self.initUI()

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
        url_label = QLabel("Тестируемый домен/IP:")
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

        # Подключаем сигналы для обновления интерфейса
        self.text_update_signal.connect(self.update_text_output)
        self.progress_update_signal.connect(self.update_progress)

    # Слот для обновления текстового поля
    def update_text_output(self, text):
        self.result_output.append(text)

    # Слот для обновления прогресса
    def update_progress(self, progress):
        self.progress_label.setText(f"Прогресс: {progress}%")

    def clear_url(self):
        self.url_input.clear()

    # Проверка правильности домена/IP, включая обработку "localhost"
    def is_valid_domain_or_ip(self, url):
        if url == "localhost":
            return "localhost"
        try:
            if "://" in url:
                url = url.split("://")[1]  # Удаляем протокол (http:// или https://)
            domain = url.split('/')[0]  # Убираем все, что после домена
            socket.gethostbyname(domain)  # Проверяем доступность домена по DNS
            return domain  # Возвращаем домен для использования
        except socket.gaierror:
            return None

    def show_invalid_url_warning(self):
        QMessageBox.warning(
            self,
            "Некорректный адрес",
            "Введите корректный домен или IP-адрес. Примеры:\n\n"
            "Домен: example.com\n"
            "IP: 192.168.0.1\n"
            "Без протокола (http/https) и слэшей (/)."
        )

    def start_scan(self):
        if self.is_scanning:
            self.text_update_signal.emit("Пентест уже запущен.")
            return

        # Получаем URL или используем "localhost", если поле пустое
        url = self.url_input.text().strip()
        if not url:
            url = "localhost"
            self.text_update_signal.emit(f"Сканирование по умолчанию запущено для {url}.")
        else:
            # Проверка правильности домена/IP
            domain = self.is_valid_domain_or_ip(url)
            if not domain:
                self.show_invalid_url_warning()
                return

            self.text_update_signal.emit(f"Начинается сканирование для {domain}...")

        self.is_scanning = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # Запуск сканирования в отдельном потоке
        self.scan_worker = ScanWorker(domain)
        self.scan_worker.progress_signal.connect(self.update_progress)
        self.scan_worker.text_signal.connect(self.update_text_output)
        self.scan_worker.finished_signal.connect(self.on_scan_finished)
        self.scan_worker.start()

    def stop_scan(self):
        if self.is_scanning:
            self.text_update_signal.emit("Остановка пентеста...")
            self.scan_worker.stop()  # Прерывание потока
            self.is_scanning = False
            self.progress_update_signal.emit(0)  # Сбрасываем прогресс на 0
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
        else:
            self.text_update_signal.emit("Пентест не запущен.")

    def on_scan_finished(self, report):
        self.is_scanning = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if report:
            # Теперь вызываем окно сохранения в основном потоке
            QTimer.singleShot(0, lambda: self.save_report(report))
        else:
            self.text_update_signal.emit("Сканирование завершено без отчета.")

    # Диалоговое окно для сохранения отчета
    def save_report(self, report):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", "", "Text Files (*.txt);;All Files (*)", options=options)

        if file_path:
            # Сохранение отчета с кодировкой UTF-8
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(report)
            self.text_update_signal.emit(f"Отчет сохранен в: {file_path}")
        else:
            self.text_update_signal.emit("Сохранение отчета отменено.")
