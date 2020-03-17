import requests  # Для работы с POST и GET
import json  # Для записи в файл JSON
import copy  # Для deepcopy
import time  # Для текущего времени
import os.path  # Для проверки существования файла

urlAmo = 'https://testcallapi.amocrm.ru'

urlAuthAmo = '/private/api/auth.php?type=json'
urlPipeAmo = '/api/v2/pipelines'
urlLeadAmo = '/api/v2/leads'

# Все данные для работы
headers = {'Content-Type': 'application/json'}

# Какой ID этапа для автообзвона
leadsStatusId = 32121847

# В какой ID этапа переносим при дозвоне
leadsStatusIdOk = 143

# В какой отдел направлять вызов
sipUri = '726@test.gravitel.ru'

# Cо скольки и до скольки автообзвон
timeFrom = '19:00'
timeTo = '20:00'

# ТОКЕН Call API
tokenCallApi = '232c7a1e8be4f3e5bded4d7fa848018f'

# Логин админа в АМО СРМ
loginUserAmo = 'nd@gravitel.ru'

# Hash этого сотрудника
hashUserAmo = '5e0db73b6bb4ddf46fcb4107090cffdcc5026961'

# Какой ТЭГ проставляем при недозвоне
tagLead = 'НЕДОЗВОН'

# Setting parameters
authKeyAmo = {'USER_LOGIN': loginUserAmo, 'USER_HASH': hashUserAmo}

# Connect with amoCRM POST

authAmo = requests.post(urlAmo + urlAuthAmo, headers=headers, json=authKeyAmo).json()

# check login & Hash

if 'error_code' in authAmo['response'].keys():
    print(authAmo['response']['error'])

# Получить все сделки, метод GET

leadKeyAmo = {'USER_LOGIN': loginUserAmo, 'USER_HASH': hashUserAmo}
leads = requests.get(urlAmo + urlLeadAmo, headers=headers, params=leadKeyAmo).json()

# Проверка на ошибки

if 'title' in leads.keys():
    print(leads['detail'])

# Делаем из словаря список словарей

leads = leads['_embedded']['items']

# Удаляем сделки, если этап не leadsStatusId

for i in reversed(range(len(leads))):
    if leads[i]['status_id'] != leadsStatusId:
        del leads[i]

# Удаляем лишние ключи

leadsClear = copy.deepcopy(leads)

for i, elem in enumerate(leads):
    for key in leads[i]:
        if key not in ('id', 'main_contact'):
            leadsClear[i].pop(key)

# Проверяем есть ли контакт у сделки, если нет, то удаляем сделку из БД.

for i in reversed(range(len(leadsClear))):
    if leadsClear[i]['main_contact'] == {}:
        del leadsClear[i]

# Достаем номер из Контакта сделки

for elem in leadsClear:
    urlContactAmo = elem['main_contact']['_links']['self']['href']
    contact = requests.get(urlAmo + urlContactAmo, headers=headers, params=leadKeyAmo).json()
    elem['main_contact'] = int(contact['_embedded']['items'][0]['custom_fields'][0]['values'][0]['value'])

    # Добавляем счетчик количества обзвонов, если его нет

    if 'count' not in elem:
        elem['count'] = 3

# Сверяем с DB_dialouts.json
if os.path.isfile('DB_dialouts.json') == True:
    with open("DB_dialouts.json", "r") as dialoutsFile:
        dbForCheck = json.load(dialoutsFile)
    dialoutsFile.close()
    for i in reversed(range(len(leadsClear))):
        for j in reversed(range(len(dbForCheck))):
            if leadsClear[i]['id'] == dbForCheck[j]['id']:
                del leadsClear[i]
    leadsClear.extend(dbForCheck)