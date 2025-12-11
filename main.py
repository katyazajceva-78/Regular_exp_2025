import re
import csv

# 1. Читаем данные из CSV-файла
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)


# Вспомогательная функция для форматирования телефона
def format_phone(phone):
    # Убираем все лишние символы, оставляя только цифры и плюс
    digits = re.sub(r'\D', '', phone)

    # Если длина номера соответствует российскому номеру мобильного
    if len(digits) == 11 and digits.startswith('8'):
        digits = digits.replace('8', '7', 1)  # Меняем 8 на 7
    elif len(digits) == 10:
        digits = '7' + digits  # Добавляем 7 впереди
    else:
        return ""  # Если номер неподходящей длины, возвращаем пустую строку

    # Формируем телефон в правильном формате
    formatted_phone = f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:]}"

    # Проверяем наличие добавочного номера
    ext_match = re.search(r'доб\s*(\d+)', phone)
    if ext_match:
        formatted_phone += f" доб.{ext_match.group(1)}"

    return formatted_phone


# Вспомогательная функция для нормального представления ФИО
def process_name(full_name):
    parts = full_name.split()  # Делим строку на части по пробелам
    while len(parts) < 3:
        parts.append("")  # Если недостаточно частей, добавляем пустые
    return parts


# Перебор и очистка данных
cleaned_contacts = []

for contact in contacts_list[1:]:  # Проходим по каждому контакту, исключив заголовок
    # Выделяем ФИО
    full_name = ' '.join(contact[:3])
    lastname, firstname, surname = process_name(full_name)

    # Остальные поля
    organization = contact[3].strip()
    position = contact[4].strip()
    phone = format_phone(contact[5])
    email = contact[6].strip()

    # Создаем новую строку
    cleaned_contacts.append([
        lastname, firstname, surname, organization, position, phone, email
    ])

# 4. Удаляем дубликаты записей
seen = {}  # Словарь для отслеживания уникальных фамилий и имен
final_contacts = [contacts_list[0]]  # Заголовок

for contact in cleaned_contacts:
    key = (contact[0], contact[1])  # Ключ по фамилии и имени
    if key not in seen:
        seen[key] = True
        final_contacts.append(contact)

# 5. Записываем очищенные данные в новый CSV-файл
with open("phonebook.csv", "w", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerows(final_contacts)