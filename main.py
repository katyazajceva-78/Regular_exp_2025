import re
import csv
from collections import defaultdict

# Читаем исходные данные
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)


# Функция для форматирования телефонных номеров
def format_phone_number(phone):
    digits = ''.join(re.findall(r'[+\d]', phone))  # извлекаем только цифры и плюс
    if len(digits) == 11 and digits.startswith('8'):
        digits = digits.replace('8', '7', 1)  # заменяем 8 на 7
    elif len(digits) == 10:
        digits = '7' + digits  # добавляем 7 впереди
    elif len(digits) != 11:
        return ''  # возвращаем пустую строку, если номер неверный

    # Формируем основную часть номера
    result = f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:]}"

    # Ищем добавочный номер
    ext_match = re.search(r'доб\.?\s*(\d+)', phone)
    if ext_match:
        result += f" доб.{ext_match.group(1)}"

    return result


# Функция для отделения ФИО
def process_name(full_name):
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
    key = (contact[0], contact[1])  # уникальное сочетание по фамилии и имени
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
final_contacts = [contacts_list[0]]  # добавляем заголовок обратно
for key, value in merged_contacts.items():
    final_row = [
        key[0],  # Lastname
        key[1],  # Firstname
        value.get('surname', ''),  # Surname (отчество)
        ', '.join(sorted(set(value['organizations']))),  # Организация
        ', '.join(sorted(set(value['positions']))),  # Должность
        ', '.join(sorted(set(value['phones']))),  # Телефон
        ', '.join(sorted(set(value['emails'])))  # Email
    ]

    # Исключаем пустые элементы только для конкретных полей
    filtered_fields = [field.strip() for field in final_row[3:] if field.strip()]  # фильтруем начиная с 4-го элемента
    final_row[3:] = filtered_fields  # заменяем старые поля новыми отфильтрованными

    final_contacts.append(final_row)

# Запись итогового результата
with open("phonebook.csv", "w", encoding="utf-8") as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows(final_contacts)