import nmap

class NmapScanner:
    def __init__(self):
        self.scanner = nmap.PortScanner()

    def run_scan(self, target):
        """
        Выполняет полное сканирование с использованием всех основных возможностей Nmap.
        target: домен или IP-адрес для сканирования.
        """
        try:
            # Полный набор аргументов Nmap
            scan_args = (
                "-A -T4 -p 1-65535 --script vuln,vulners,default "
                "--open --osscan-guess --version-all --top-ports 1000"
            )
            
            # Выполняем сканирование
            self.scanner.scan(target, arguments=scan_args)

            # Если хостов нет, вернуть None
            if not self.scanner.all_hosts():
                return None

            # Формируем отчет о сканировании
            report = self.generate_report()
            return report

        except Exception as e:
            return f"Ошибка при запуске сканирования: {e}"

    def generate_report(self):
        """
        Формирует отчет на основе результатов сканирования.
        """
        report = ""
        for host in self.scanner.all_hosts():
            report += f"Хост: {host} ({self.scanner[host].hostname()})\n"
            report += f"Статус: {self.scanner[host].state()}\n"

            # Определение операционной системы
            if 'osclass' in self.scanner[host]:
                for osclass in self.scanner[host]['osclass']:
                    report += f"ОС: {osclass['osfamily']} {osclass['osgen']} ({osclass['accuracy']}%)\n"

            # Определение версий сервисов
            for proto in self.scanner[host].all_protocols():
                report += f"\nПротокол: {proto}\n"
                ports = self.scanner[host][proto].keys()
                for port in ports:
                    report += f"Порт: {port}\tСостояние: {self.scanner[host][proto][port]['state']}\n"
                    report += f"Сервис: {self.scanner[host][proto][port]['name']}\n"
                    if 'product' in self.scanner[host][proto][port]:
                        report += f"Продукт: {self.scanner[host][proto][port]['product']}\n"
                    if 'version' in self.scanner[host][proto][port]:
                        report += f"Версия: {self.scanner[host][proto][port]['version']}\n"
                    
                    # Уязвимости
                    if 'script' in self.scanner[host][proto][port]:
                        report += "Найденные уязвимости:\n"
                        for script_name, script_output in self.scanner[host][proto][port]['script'].items():
                            report += f"Скрипт: {script_name}\nРезультат: {script_output}\n\n"
        
        return report
