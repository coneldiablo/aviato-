import nmap

class NmapScanner:
    def __init__(self):
        self.scanner = nmap.PortScanner()

    def run_scan(self, target="localhost"):
        try:
            # Запуск Nmap для указанного target
            print(f"Запуск Nmap для цели: {target}")
            self.scanner.scan(target, arguments='-A -T4')
            
            # Проверяем, нашел ли Nmap какие-то хосты
            if not self.scanner.all_hosts():
                return "Сканирование завершено, но хосты не найдены."
            
            # Формируем отчет
            report = ""
            for host in self.scanner.all_hosts():
                report += f"Хост: {host} ({self.scanner[host].hostname()})\n"
                report += f"Статус: {self.scanner[host].state()}\n"
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
                        report += "\n"
            return report
        except Exception as e:
            return f"Ошибка при запуске сканирования: {str(e)}"
