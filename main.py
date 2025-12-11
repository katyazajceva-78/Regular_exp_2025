import re
import csv
from collections import defaultdict

# Читаем исходные данные
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)


# Функция для форматирования телефонных номеров
def format_phone_number(phone):
    """Преобразует телефонный номер в нужный формат."""
    digits = ''.join(re.findall(r'[+\d]', phone))  # извлекаем только цифры и знак +
    if len(digits) == 11 and digits.startswith('8'):
        digits = digits.replace('8', '7', 1)  # меняем 8 на 7
    elif len(digits) == 10:
        digits = '7' + digits  # добавляем префикс +7
    elif len(digits) != 11:
        return ''  # неправильный формат номера

    # формируем базовый формат номера
    result = f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:]}"

    # ищем добавочный номер
    ext_match = re.search(r'доб\.?\s*(\d+)', phone)
    if ext_match:
        result += f" доб.{ext_match.group(1)}"

    return result


# Функция для правильного распределения ФИО
def process_name(full_name):
    """Распределяет ФИО по компонентам (Lastname, Firstname, Surname)."""
    names = full_name.split()
    while len(names) < 3:
        names.append('')
    return names


# Основная логика обработки
normalized_contacts = []

for row in contacts_list[1:]:  # пропускаем заголовок
    full_name = ' '.join(row[:3])
    lastname, firstname, surname = process_name(full_name)
    organization = row[3].strip()
    position = row[4].strip()
    phone = format_phone_number(row[5])
    email = row[6].strip()
    normalized_contacts.append([lastname, firstname, surname, organization, position, phone, email])

# Удаление дубликатов с сохранением отчества
merged_contacts = defaultdict(dict)

for contact in normalized_contacts:
    key = (contact[0], contact[1])  # Уникальность по фамилии и имени
    if key not in merged_contacts:
        merged_contacts[key]['surname'] = contact[2]
        merged_contacts[key]['organizations'] = []
        merged_contacts[key]['positions'] = []
        merged_contacts[key]['phones'] = []
        merged_contacts[key]['emails'] = []

    merged_contacts[key]['organizations'].append(contact[3])
    merged_contacts[key]['positions'].append(contact[4])
    merged_contacts[key]['phones'].append(contact[5])
    merged_contacts[key]['emails'].append(contact[6])

# Сбор финальной таблицы
final_contacts = [contacts_list[0]]  # Добавляем заголовок обратно
for key, value in merged_contacts.items():
    final_row = [
        key[0],  # Lastname
        key[1],  # Firstname
        value.get('surname', ''),  # Surname (отчество)
        ', '.join(sorted(set(value['organizations']))),  # Организации
        ', '.join(sorted(set(value['positions']))),  # Должности
        ', '.join(sorted(set(value['phones']))),  # Телефоны
        ', '.join(sorted(set(value['emails'])))  # Emails
    ]

    # Исключаем пустые элементы из объединяемых строк
    final_row = [item.strip() for item in final_row if item.strip()]

    final_contacts.append(final_row)

# Запись итогового результата
with open("phonebook.csv", "w", encoding="utf-8") as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows(final_contacts)