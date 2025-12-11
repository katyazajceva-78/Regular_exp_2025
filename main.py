import re
import csv
from collections import defaultdict

# Читаем адресную книгу в формате CSV в список contacts_list
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)


# Функция для форматирования телефонных номеров
def format_phone_number(phone):
    """
    Преобразует телефонный номер в стандартный формат +7(999)999-99-99 или +7(999)999-99-99 доб.9999
    """
    # Очищаем строку от символов, кроме чисел и '+' в начале
    digits = ''.join(re.findall(r'[+\d]', phone))

    # Проверяем длину строки и определяем тип телефона
    if len(digits) == 11 and digits.startswith('+'):
        main_part = digits[1:]
    elif len(digits) == 11 and digits.startswith('8'):
        main_part = digits[1:]
    elif len(digits) == 10:
        main_part = digits
    else:
        return ''  # Неправильный формат телефона

    # Формируем основной формат номера
    formatted_phone = f'+7({main_part[:3]}){main_part[3:6]}-{main_part[6:8]}-{main_part[8:]}'

    # Добавляем добавочный номер, если он указан
    ext_match = re.search(r'доб\.*\s*(\d+)', phone)
    if ext_match:
        formatted_phone += f' доб.{ext_match.group(1)}'

    return formatted_phone


# Функциональность для разделения ФИО
def separate_full_name(full_name):
    """
    Распределяет имя, фамилию и отчество по отдельным элементам списка.
    """
    parts = full_name.strip().split(maxsplit=2)
    while len(parts) < 3:
        parts.append('')
    return parts


# Применяем очистку и нормализацию данных
normalized_contacts = []

for row in contacts_list[1:]:  # Пропускаем заголовок
    # Отделяем ФИО
    full_name = ' '.join(row[:3])
    lastname, firstname, surname = separate_full_name(full_name)

    # Получаем остальную информацию
    organization = row[3].strip()
    position = row[4].strip()
    phone = format_phone_number(row[5])
    email = row[6].strip()

    # Создаем новую нормализованную запись
    new_row = [lastname, firstname, surname, organization, position, phone, email]
    normalized_contacts.append(new_row)

# Группируем записи по ФИО и удаляем дубликаты
merged_contacts = defaultdict(lambda: {'organization': [], 'position': [], 'phones': [], 'emails': []})

for record in normalized_contacts:
    key = (record[0], record[1])  # Ключ по фамилии и имени
    entry = merged_contacts[key]
    entry['organization'].append(record[3])
    entry['position'].append(record[4])
    entry['phones'].append(record[5])
    entry['emails'].append(record[6])

# Готовим итоговую таблицу
final_contacts = [contacts_list[0]]  # добавляем заголовок обратно
for key, values in merged_contacts.items():
    # Оставляем уникальные организации, должности, телефоны и почты
    organizations = ', '.join(set(values['organization']))
    positions = ', '.join(set(values['position']))
    phones = ', '.join(set(filter(None, values['phones'])))
    emails = ', '.join(set(filter(None, values['emails'])))

    # Собираем строку
    final_row = [key[0], key[1], '', organizations, positions, phones, emails]
    final_contacts.append(final_row)

# Запись результатов в новый CSV-файл
with open("phonebook.csv", "w", encoding="utf-8") as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows(final_contacts)