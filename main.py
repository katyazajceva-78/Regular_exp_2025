import re
from collections import defaultdict
import csv


def normalize_name(name):
    """Разделение строки с именем на составляющие"""
    parts = name.split()
    if len(parts) > 3:
        return ' '.join(parts[:3])
    elif len(parts) == 3:
        return ' '.join(parts)
    else:
        return ' '.join(parts)


def normalize_phone(phone):
    """Преобразование телефона в стандартный формат"""
    pattern = r'(\+?\d)?\D*(\d{3})\D*(\d{3})\D*(\d{2})\D*(\d{2})(?:\s*(доб\.?)?\s*(\d+)?)?'
    match = re.match(pattern, phone)
    if not match:
        return ''
    groups = match.groups()
    normalized_number = '+7({code_area})-{number}'.format(
        code_area=groups[1],
        number='-'.join([groups[2], groups[3], groups[4]])
    )
    if groups[-1]:
        normalized_number += ' доб.' + groups[-1]
    return normalized_number.strip()


def clean_contacts(data):  # переименовали аргумент
    """Главная логика очистки и объединения записей"""
    result = []
    headers = data.pop(0)
    grouped_data = defaultdict(list)

    for record in data:  # используем другое имя переменной
        full_name = normalize_name(' '.join(record[:3]))
        key = tuple(full_name.split())
        grouped_data[key].append({
            'lastname': record[0],
            'firstname': record[1],
            'surname': record[2],
            'organization': record[3],
            'position': record[4],
            'phone': normalize_phone(record[5]),
            'email': record[6]
        })

    for key, records in grouped_data.items():
        merged_record = {}
        for field in ['lastname', 'firstname', 'surname']:
            values = set(r[field] for r in records)
            merged_record[field] = max(values, key=lambda x: len(x)) if values else ""

        for field in ['organization', 'position', 'email']:
            non_empty_values = [r[field] for r in records if r[field]]
            merged_record[field] = non_empty_values[0] if non_empty_values else ""

        phones = {normalize_phone(r['phone']) for r in records}
        merged_record['phone'] = ', '.join(sorted(phones))

        result.append(merged_record.values())

    return [headers] + sorted(result, key=lambda row: next(iter(row)))


if __name__ == "__main__":
    raw_csv_filename = 'phonebook_raw.csv'
    processed_csv_filename = 'phonebook.csv'

    with open(raw_csv_filename, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',')
        contacts_list = list(reader)  # сохранили глобальную переменную

    cleaned_contacts = clean_contacts(contacts_list)  # передали ей в функцию

    with open(processed_csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(cleaned_contacts)

    print("Контакты успешно обработаны!")