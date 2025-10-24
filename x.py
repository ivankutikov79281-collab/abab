from fastapi import FastAPI, Cookie, Depends, Form, Request, Query
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse, RedirectResponse
from jinja2 import Template
from typing import Dict, Any, Optional
import uvicorn
import requests
import random as rnd
import json
import pandas as pd
from pydantic import BaseModel
from typing import Optional

app =  FastAPI()
FILEPATH = 'cache.csv'


def dict_to_string(d):
    return json.dumps(d, sort_keys=True, ensure_ascii=False)

def cheсk_cache(string):
    try:
        df = pd.read_csv(FILEPATH, header=None, names=['string', 'sankey_html1', 'sankey_html2'])
        print("len(cache.csv)", len(df))
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame(columns=['string', 'sankey_html1', 'sankey_html2', ])
        df.to_csv(FILEPATH, header=False, index=False, encoding='utf-8')
    finding_in_cache = df[df.string == string]
    print("finding_in_cache", finding_in_cache)
    if len(finding_in_cache) == 0:
        df = pd.concat([df, pd.DataFrame({'string': [string], 'sankey_html1': [''], 'sankey_html2': [''], }) ])
        df.to_csv(FILEPATH, header=False, index=False, encoding='utf-8')
        return '', ''
    else:
        return finding_in_cache.iloc[0]['sankey_html1'], finding_in_cache.iloc[0]['sankey_html2']
    

def sent_message(text):
    BOT_TOKEN = "8445738943:AAHcZYGAtt2UTbTZj3jGaDKTJy49yoa_WqE"
    print(-1002916176207)
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": -1002916176207, "text": f'zapros_snaky${rnd.randint(1, 100_000)}$&' + str(text)})
    print(-4821667868)
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": -4821667868, "text": f'zapros_snaky${rnd.randint(1, 100_000)}$&' + str(text)})
    print(3)

@app.get("/current_queries", response_class=HTMLResponse)
def current_queries():
    with open(FILEPATH, 'r', encoding='utf-8') as file:
        content = file.read()
    return content
    


class SankeyRequest(BaseModel):
    string: str  # ваш JSON строка
    sankey_html1: str
    sankey_html2: Optional[str] = None

@app.post("/add_sankey_answer", response_class=HTMLResponse)
async def add_sankey_answer(request: SankeyRequest):
    print("/add_sankey_answer")
    string = request.string
    sankey_html1 = request.sankey_html1.replace("/", "")
    sankey_html2 = request.sankey_html2.replace("/", "")
    print(f"Received data: {request.string}")
    print(f"Sankey HTML2 length: {len(request.sankey_html1)}")
    print(f"Sankey HTML2 length: {len(request.sankey_html2)}")
    df = pd.read_csv(FILEPATH, header=None, names=['string', 'sankey_html1', 'sankey_html2'])
    finding_in_cache = df[df.string == string]
    if (df['string'] == string).sum() > 0:
        df.loc[df['string'] == string, ['sankey_html1', 'sankey_html2']] = sankey_html1, sankey_html2
    else:
        df = pd.concat([df, pd.DataFrame({'string': [string], 'sankey_html1': [sankey_html1], 'sankey_html2': [sankey_html2], })]).fillna("")
    df.to_csv(FILEPATH, header=False, index=False, encoding='utf-8')
    return 'complete'

@app.get("/a", response_class=HTMLResponse)
def fa():
    return "urrrrrraaaaaa~!!!!!!"

from fastapi import Request, Query
from fastapi.templating import Jinja2Templates
from typing import Optional
import os

# Инициализация шаблонов
templates = Jinja2Templates(directory="templates")

from fastapi import Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from datetime import datetime

# Инициализация шаблонов
templates = Jinja2Templates(directory=".")

@app.get("/")
async def dashboard(
    request: Request,
    # Параметры фильтров с значениями по умолчанию
    date: Optional[str] = Query(None),
    granularity: Optional[str] = Query("Месяц"),
    tourType: Optional[str] = Query("Все"),
    country: Optional[str] = Query("Все"),
    platform: Optional[str] = Query("Все"),
    # Параметры чекбоксов
    visitedPages_mainBeforeListing: Optional[bool] = Query(False),
    visitedPages_articleBeforeListing: Optional[bool] = Query(False),
    visitedPages_eBeforeListing: Optional[bool] = Query(False),
    usedFeatures_searchOpened: Optional[bool] = Query(False),
    usedFeatures_filterOpened: Optional[bool] = Query(False),
    usedFeatures_bookingViaQuestion: Optional[bool] = Query(False)
):
    # Устанавливаем дату по умолчанию если не передана
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Собираем все значения фильтров
    filter_values = {
        "date": date,
        "granularity": granularity,
        "tourType": tourType,
        "country": country,
        "platform": platform,
        "visitedPages_mainBeforeListing": visitedPages_mainBeforeListing,
        "visitedPages_articleBeforeListing": visitedPages_articleBeforeListing,
        "visitedPages_eBeforeListing": visitedPages_eBeforeListing,
        "usedFeatures_searchOpened": usedFeatures_searchOpened,
        "usedFeatures_filterOpened": usedFeatures_filterOpened,
        "usedFeatures_bookingViaQuestion": usedFeatures_bookingViaQuestion
    }
    
    # Проверяем, это AJAX-запрос (ожидаем JSON) или обычная загрузка
    accept_header = request.headers.get("accept", "")
    is_ajax = "application/json" in accept_header
    
    # Обрабатываем данные на основе фильтров
    processed_data = process_filters(**filter_values)
    sankey_html1, sankey_html2 = generate_sankey_html(processed_data)
    if is_ajax:
        # AJAX-запрос - возвращаем JSONResponse
        return JSONResponse({
            "zagolovok": f"Данные за {date}",
            "sankey_html1": sankey_html1,
            "sankey_html2": sankey_html2,
        })
    else:
        # Обычная загрузка страницы - используем Jinja2 templates
        data = {
            'request': request,
            'zagolovok': 'Мой сайт',
            "sankey_html1": sankey_html1,
            "sankey_html2": sankey_html2,
            'filter_values': filter_values,
        }
        
        return templates.TemplateResponse("dashboard.html", data)

def process_filters(**kwargs):
    
    print("Обрабатываем фильтры:", kwargs)
    return {
        "data": "processed_data_based_on_filters",
        "filters_applied": kwargs
    }

def generate_sankey_html(data):
    # Ваша логика генерации Sankey диаграммы
    string = dict_to_string(data)
    sankey_html1, sankey_html2 = cheсk_cache(string)
    if sankey_html1 == "":
        sankey_html1 = 'Происходит обработка дэшборда до заказа. Ожидайте 1-4 минуты'
        sankey_html2 = 'Происходит обработка дэшборда после заказа. Ожидайте 1-4 минуты'
    return f"<div class='sankey-chart'>{sankey_html1}<br>Sankey Diagram 1 based on: {string}</div>", f"<div class='sankey-chart'>{sankey_html2}<br>Sankey Diagram 2 based on: {data['filters_applied']}</div>"



@app.get("/dashboard")
async def get_dashboard_data(request: Request):
    pass


@app.get("/request_dashboard_from_parameters/")
async def get_dashboard_data(request: Request):
    sent_message('go get_dashboard_data')
    # Получаем все query параметры
    query_params = dict(request.query_params)
    print("Все query параметры:", query_params)
    
    # Словарь для результата
    filters = {}
    
    def parse_nested_key(key):
        """Парсит ключи вида 'parent[child]' или 'parent[child][grandchild]'"""
        if '[' in key and ']' in key:
            # Извлекаем основное имя и вложенные ключи
            main_key = key.split('[')[0]
            sub_keys = key[len(main_key):].strip('[]').split('][')
            return main_key, sub_keys
        return key, []
    
    def convert_value(value):
        """Преобразует строковые значения в соответствующие типы"""
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        elif value.isdigit():
            return int(value)
        elif value.replace('.', '').isdigit():
            return float(value)
        return value
    
    def set_nested_value(obj, keys, value):
        """Устанавливает значение во вложенной структуре по цепочке ключей"""
        current = obj
        for i, key in enumerate(keys[:-1]):
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    for key, value in query_params.items():
        print(f"Обработка параметра: {key} = {value}")
        
        # Обрабатываем вложенные объекты (visitedPages[mainBeforeListing] и т.д.)
        if '[' in key and ']' in key:
            main_key, sub_keys = parse_nested_key(key)
            converted_value = convert_value(value)
            
            # Создаем основную структуру если её нет
            if main_key not in filters:
                filters[main_key] = {}
            
            # Устанавливаем значение во вложенной структуре
            set_nested_value(filters, [main_key] + sub_keys, converted_value)
        else:
            # Простые ключи
            filters[key] = convert_value(value)
    
    print("Полученные фильтры:", filters)
    
    # Валидация и преобразование структуры к ожидаемому формату
    expected_filters = {
        "date": filters.get("date", ""),
        "granularity": filters.get("granularity", ""),
        "tourType": filters.get("tourType", ""),
        "country": filters.get("country", ""),
        "platform": filters.get("platform", ""),
        "visitedPages": {
            "mainBeforeListing": filters.get("visitedPages", {}).get("mainBeforeListing", False),
            "articleBeforeListing": filters.get("visitedPages", {}).get("articleBeforeListing", False),
            "eBeforeListing": filters.get("visitedPages", {}).get("eBeforeListing", False)
        },
        "usedFeatures": {
            "searchOpened": filters.get("usedFeatures", {}).get("searchOpened", False),
            "filterOpened": filters.get("usedFeatures", {}).get("filterOpened", False),
            "bookingViaQuestion": filters.get("usedFeatures", {}).get("bookingViaQuestion", False)
        }
    }
    
    print("Обработанные фильтры:", expected_filters)
    
    def find_in_cache_map(expected_filters):
        string = dict_to_string(expected_filters)
        sankey_html1, sankey_html2 = cheсk_cache(string) # на этом этапе добавляются пыстые строки
        if sankey_html1 == "":
            sent_message(expected_filters)
        else:
            pass
        
    
    # Здесь ваша логика обработки данных
    # Например, вызов функции для получения данных дашборда
    # dashboard_data = await get_dashboard_data_from_db(expected_filters)
    
    
    return JSONResponse({
        "status": "success",
        "filters": expected_filters,
        "message": "Данные успешно получены",
        "received_params": query_params  # для отладки
    })



if __name__ == '__main__':
    uvicorn.run('x:app', port=8000, host='217.26.28.84', reload=True)

