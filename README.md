# Парсер для сайта dom.mingkh.ru
## Требования для запуска 
* python3
* Virtual environment (Опционально)

## Установка дополнительных библиотек
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Запуск
Получение справки
```
python main.py -h
```
Получение списка городов в регионе
```
python main.py -s chukotstiy-ao -l
```
Загрузка данных по всем городам по региону
```
python main.py -s chukotstiy-ao
```

Загрузка данных по определенному городу и региону
```
python main.py -s chukotskiy-ao -c omolon
```
После завершения работы скрипта в текущей папке появится файл формата CSV с данными