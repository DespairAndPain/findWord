import os
from flask import Flask, request, redirect, url_for, render_template
import zipfile
import re

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')
UPLOAD_FOLDER = '/media/owner/OS_Install/Proj/py/test2/static'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def render():
    return render_template('home.html')

# сохраняем файл с обучающей выборкой
@app.route('/train', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'train.zip'))
            return redirect('/')
    return 'yes'

# сохраняем файл с тестовой выборкой
@app.route('/test', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'test.zip'))
            return redirect('/')
    return 'yes'


@app.route('/file')
def open():
    trainCol = {}
    # открываю файл с обучением
    with zipfile.ZipFile(os.path.join(APP_STATIC, 'train.zip'), 'r') as myzip:
        with myzip.open('[[train.dat]]', 'r') as myfile:
            n = 0
            # по строчке
            for line in myfile:
                if n == 1:
                    # сохраняем первый символ с строке
                    first = line.decode('utf-8')[0]
                    # затем вытаскиваем все остальные по паттерну ", [число]"
                    # в результате получается подобное: [1,0,1,1,0,1]
                    newLine = re.findall(r'\W\W\d\W', line.decode('utf-8'))
                    newNewLine = []
                    # потом по строке объединяем в list который записываем в collection
                    newNewLine.append(first)
                    for item in newLine:
                        result = re.search(r'\d' ,item)
                        newNewLine.append(result.group(0))
                        trainCol[''+newNewLine[-1]+''] = newNewLine[0:-1]
                    print(newNewLine)

                    # работаем с текстом после тега @data
                else:
                    if '@data' in line.decode("utf-8"):
                        n = 1
    # Аналогично для тестовой
    testCol = {}
    with zipfile.ZipFile(os.path.join(APP_STATIC, 'test.zip'), 'r') as myzip:
        with myzip.open('[[test.dat]]', 'r') as myfile:
            n = 0
            for line in myfile:
                if n == 1:
                    newLine = re.findall(r'\W\W\d\W', line.decode('utf-8'))
                    newNewLine = []

                    for item in newLine:
                        result = re.search(r'\d' ,item)
                        newNewLine.append(result.group(0))
                        testCol[''+newNewLine[-1]+''] = newNewLine[0:-1]

                else:
                    if '@data' in line.decode("utf-8"):
                        n = 1

    eq = 0
    max = {}
    maxNumb = []
    mark = 0

    # Затем сравниваем оба словаря, берём тестовую и прогоняем по всем обучающим строкам
    for tc in testCol:
        for trc in trainCol:
            n = 0
            for i in tc[1]:
                # Если находим схожесть то записывам в переменную количество схожих символов "eq"
                if tc[1][n] == trc[1][n]:
                    eq += 1
                n += 1

            if eq > maxNumb[0]:
                maxNumb = [eq, trc[0], trc[1]]
            eq = 0
        # В конце цикла по обучающей выборке записываем в словарь строку из тестовой и массив
        # из количества схоэих эллементов, метки класса, самой строки из
        # обучающей выборки в которой наибольшее количетов
        # похожих эллементов
        max[''+str(tc[1])+''] = maxNumb
    # В итоге должен получится словарь с исходной строкой, количетвом схожестей, меткой класса и стракой для сравнения
    # Это можно засунуть в контекст и в итоге вывести

    # Но работет это всё при условии что в обучающей выборке будут уникальные идентификаторы класса
    # для каждого набора атрибутов
    return render_template('open.html')




if __name__ == '__main__':
    app.run()

