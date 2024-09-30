import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(report):
    # Данные для авторизации
    from_addr = 'melartiooowr334@gmail.com'  # Ваш email
    password = 'magomed16'  # Пароль от вашего email (или пароль приложения)
    
    # Кому отправляем отчет
    to_addr = 'melartiooowr334@gmail.com'

    # Создаем объект сообщения
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = 'Отчет о пентесте'

    # Тело письма
    body = 'Пожалуйста, найдите приложенный отчет о пентесте.'
    msg.attach(MIMEText(body, 'plain'))

    # Вложение — отчет в виде текстового файла
    attachment = MIMEText(report, 'plain')
    attachment.add_header('Content-Disposition', 'attachment', filename='pentest_report.txt')
    msg.attach(attachment)

    # Настройка SMTP-сервера для Gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()  # Начинаем защищённое соединение
    server.login(from_addr, password)  # Входим в аккаунт
    text = msg.as_string()  # Преобразуем сообщение в строку
    server.sendmail(from_addr, to_addr, text)  # Отправляем письмо
    server.quit()  # Закрываем соединение
