import re
import csv
from collections import defaultdict

# Читаем исходные данные
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)


# Функция для форматирования телефонных номеров
def format_phone_number(phone):
    digits = ''.join(re.findall(r'[+\d]', phone))  # вытаскиваем только цифры и плюс
    if len(digits) == 11 and digits.startswith('8'):
        digits = digits.replace('8', '7', 1)  # заменяем 8 на 7
    elif len(digits) == 10:
        digits = '7' + digits  # добавляем 7 впереди
    elif len(digits) != 11:
        return ''  # неправильный формат номера

    result = f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:]}"  # общий формат телефона

    # проверяем наличие добавочного номера
    ext_match = re.search(r'доб\.?\s*(\d+)', phone)
    if ext_match:
        result += f" доб.{ext_match.group(1)}"

    return result


# Функция для нормальной обработки ФИО
def process_name(full_name):
    names = full_name.split()
    while len(names) < 3:
        names.append('')
    return names


# Начнем подготовку новых данных
new_contacts = []

for row in contacts_list[1:]:  # начинаем со второй строки, пропускаем заголовок
    # выделяем ФИО
    full_name = ' '.join(row[:3])
    lastname, firstname, surname = process_name(full_name)

    # остальные поля
    organization = row[3].strip()
    position = row[4].strip()
    phone = format_phone_number(row[5])
    email = row[6].strip()

    # создаем новый контакт
    new_contacts.append([lastname, firstname, surname, organization, position, phone, email])

# Удаляем дубликаты, объединяя схожие записи
merged_contacts = defaultdict(lambda: {
    'organizations': [],
    'positions': [],
    'phones': [],
    'emails': []
})

for contact in new_contacts:
    key = (contact[0], contact[1])  # ключ по фамилии и имени
    merged_contacts[key]['organizations'].append(contact[3])
    merged_contacts[key]['positions'].append(contact[4])
    merged_contacts[key]['phones'].append(contact[5])
    merged_contacts[key]['emails'].append(contact[6])

# Финальная подготовка данных
final_contacts = [contacts_list[0]]  # заголовок

for key, values in merged_contacts.items():
    final_row = [
        key[0],  # фамилия
        key[1],  # имя
        '',  # пока оставляем отчество пустым (его можно вернуть позже)
        ', '.join(set(values['organizations'])),  # уникальные организации
        ', '.join(set(values['positions'])),  # уникальные должности
        ', '.join(set(values['phones'])),  # уникальные телефоны
        ', '.join(set(values['emails']))  # уникальные е-мэйлы
    ]
    final_contacts.append(final_row)

# Записываем итоговый результат
with open("phonebook.csv", "w", encoding="utf-8") as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows(final_contacts)