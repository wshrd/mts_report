import os
import PyPDF2
import re
import csv
# Функция для извлечения текста из PDF файла
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        # Проходим по всем страницам и извлекаем текст
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text
# Функция для извлечения определенных строк из текста
def extract_specific_lines_from_text(text):
    lines = text.splitlines()
    # Ищем строки, начинающиеся с определенных фраз
    komu = next((line for line in lines if line.startswith('Кому:')), None)
    nds = next((line for line in lines if 'В том числе налоги:' in line), None)
    itogo = next((line for line in lines if 'Израсходовано за период:' in line), None)
    return komu, nds, itogo
# Функция для извлечения значений из найденных строк
def extract_values_from_lines(komu, nds, itogo):
    # Используем регулярные выражения для извлечения значений
    komu_value = re.search(r'(?<=Кому: ).*', komu).group()
    nds_value = re.search(r'(?<=В том числе налоги: ).*', nds).group()
    itogo_value = re.search(r'(?<=Израсходовано за период: ).*', itogo).group()
    # Извлекаем числа с плавающей точкой из строк
    numbers1 = re.findall(r'\d+,\d+', nds_value)
    numbers2 = re.findall(r'\d+,\d+', itogo_value)
    # Преобразуем формат чисел из строки во float, заменяя запятую на точку
    numbers1 = [float(number.replace(',', '.')) for number in numbers1]
    numbers2 = [float(number.replace(',', '.')) for number in numbers2]
    nds_value = numbers1
    itogo_value = numbers2
    # Возвращаем обработанные значения
    return komu_value, nds_value, itogo_value
# Получить список всех файлов в директории
directory = '/home/adm1n/Downloads/pdf/'
output_file = '/home/adm1n/Downloads/output.csv'
output_array = []
output_dict = {}
# Проходим по всем файлам в указанной директории
for filename in os.listdir(directory):
    # Обрабатываем только PDF файлы
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(directory, filename)
        # Извлекаем текст из каждого PDF файла
        pdf_text = extract_text_from_pdf(pdf_path)
        # Извлекаем специфические строки из текста
        komu, nds, itogo = extract_specific_lines_from_text(pdf_text)
        # Извлекаем значения из этих строк
        komu_value, nds_value, itogo_value = extract_values_from_lines(komu, nds, itogo)
        # Добавляем извлеченные значения в массив для последующей записи в CSV
        output_array.append([komu_value, sum(nds_value), sum(itogo_value)]) 
# Собираем данные в словарь для агрегации по ключу (Кому)
for item in output_array:
    key = item[0]
    if key in output_dict:
        output_dict[key][1] += item[1]
        output_dict[key][2] += item[2]
    else:
        # Если ключа нет, добавляем новую запись
        output_dict[key] = [item[0], item[1], item[2]]
# Преобразуем словарь обратно в массив для записи в CSV
output_array = list(output_dict.values())
# Записываем данные в CSV файл
with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    # Записываем строки в CSV файл
    writer.writerows(output_array)