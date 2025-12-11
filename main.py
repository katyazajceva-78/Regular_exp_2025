import re
import csv
from collections import defaultdict

# Открываем исходный CSV-файл
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)


# Функция для форматирования телефонных номеров
def format_phone_number(phone):
    digits = ''.join(re.findall(r'[+\d]', phone))  # чистим номер от посторонних символов
    if len(digits) == 11 and digits.startswith('8'):
        digits = digits.replace('8', '7', 1)  # замена 8 на 7
    elif len(digits) == 10:
        digits = '7' + digits  # добавляем код страны
    elif len(digits) != 11:
        return ''  # неверный формат номера

    # формируем номер в общем формате
    result = f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:]}"

    # проверяем наличие добавочного номера
    ext_match = re.search(r'доб\.?\s*(\d+)', phone)
    if ext_match:
        result += f" доб.{ext_match.group(1)}"

    return result


# Функция для обработки ФИО
def process_name(full_name):
    names = full_name.split()
    while len(names) < 3:
        names.append('')
    return names


# Подготовим нормализованные данные
normalized_contacts = []

for row in contacts_list[1:]:  # пропускаем заголовок
    # Обрабатываем ФИО
    full_name = ' '.join(row[:3])
    lastname, firstname, surname = process_name(full_name)

    # Остальные поля
    organization = row[3].strip()
    position = row[4].strip()
    phone = format_phone_number(row[5])
    email = row[6].strip()

    # Новая запись
    normalized_contacts.append([lastname, firstname, surname, organization, position, phone, email])

# Удаляем дубликаты и объединяем похожие записи
merged_contacts = defaultdict(lambda: {
    'organizations': [],
    'positions': [],
    'phones': [],
    'emails': []
})

for contact in normalized_contacts:
    key = (contact[0], contact[1])  # ключевое поле - фамилия и имя
    merged_contacts[key]['organizations'].append(contact[3])
    merged_contacts[key]['positions'].append(contact[4])
    merged_contacts[key]['phones'].append(contact[5])
    merged_contacts[key]['emails'].append(contact[6])

# Создание итоговой таблицы
final_contacts = [contacts_list[0]]  # заголовок остается прежним

for key, values in merged_contacts.items():
    final_row = [
        key[0],  # фамилия
        key[1],  # имя
        '',  # отчество (оставлено пустым, можно дополнить позже)
        ', '.join(set(item for item in values['organizations'] if item)),  # только непустые организации
        ', '.join(set(item for item in values['positions'] if item)),  # только непустые должности
        ', '.join(set(item for item in values['phones'] if item)),  # только непустые телефоны
        ', '.join(set(item for item in values['emails'] if item))  # только непустые мейлы
    ]
    final_contacts.append(final_row)

# Записываем результаты в новый CSV-файл
with open("phonebook.csv", "w", encoding="utf-8") as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows(final_contacts)