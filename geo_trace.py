#!/usr/bin/env python3
# coding: utf-8

""" Программа для визуальной трассировки маршрута.
    При запуске, обрабатывает введенный ip - адрес или хост и выводит
    в браузере карту маршрута, где начальная точка(ваш IP) - обозначен зеленым
    цветом, конечная(IP назначения) - красным, промежуточные IP(hops) - синим
    и указаны линии маршрута."""


import geocoder
import pexpect
import pandas as pd
import folium


# Начало проекта
data = input('Введите хост или ip адрес для трассировки маршрута: ')

# С помощью модуля pexpect, выполняем команду трассировки маршрута и записываем его в файл csv
shell_cmd = f'mtr -C -n {data} > tracer_files.csv'
trace = pexpect.spawn('/bin/bash', ['-c', shell_cmd])
trace.expect(pexpect.EOF)

# Считываем файл с помощью pandas
df = pd.read_csv('tracer_files.csv', usecols=[5])

# Затем очищаем столбец от ненужных данных
select = df['Ip'] == '???'
ip_sel = df[~select]

# Убираем числовые индексы
ip = ip_sel.set_index('Ip')

# Затем переводим объект DataFrame в список
ip_list = ip.index.to_list()
print(ip_list)

lists = []                                              # Создаем пустой список
for i in range(len(ip_list)):                           # С помощью цикла for, добавляем в список все ip адреса маршрута
    g = geocoder.ip(ip_list[i])
    lists.append(g.latlng)
lists[:] = [item for item in lists if item != []]       # Очищаем список от пустых значений

# Конвертируем список lists в объект DataFrame, и, устанавливаем название столбцов
table_ip = pd.DataFrame(lists, columns=['latitude', 'longitude']).dropna()

# Присваиваем значение каждого столбца переменным
lat = table_ip['latitude']
lng = table_ip['longitude']
index = table_ip.index

m = folium.Map(location=lists[0], tiles='Stamen Terrain')  # Открываем интерактивную карту
# Выставляем начальный маркер
k = folium.Marker(location=lists[0], popup=f'<i>My_host. ip - {ip_list[2]}</i>', tooltip=lists[2],
                  icon=folium.Icon(color='green'))
k.add_to(m)

# Присваиваем значение среза списка lists, переменной res_list
res_list = lists[:-2]
ip_index = ip_list[:-2]

for res, res_ip in zip(res_list, ip_index):                  # Распаковываем объекты из списка
    k = folium.CircleMarker(location=res, radius=10, popup=f'<i>{res_ip}</i>',
                            tooltip=res, fill_color='blue')  # Выводим маркеры, начиная с 3 элемента списка
    k.add_to(m)                                              # И заканчивая предпоследним

# Выставляем конечный маркер
folium.Marker(location=lists[-1], popup=f'<i>{data}. ip - {ip_list[-1]}</i>', tooltip=lists[-1],
              icon=folium.Icon(color='red')).add_to(m)

# Обратно конвертируем объект DataFrame в список
s = table_ip.set_index(['latitude', 'longitude']).to_records().tolist()

folium.PolyLine(locations=s, color="red", weight=2.5, opacity=1).add_to(m)  # Соединяем маркеры линиями

m.save('trace_files.html')                                                  # Сохраняем карту в формате html
pexpect.run('google-chrome trace_files.html')                               # Запускаем сохраненный файл в браузере

