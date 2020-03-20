import requests  # Для работы с POST и GET
import json  # Для записи в файл JSON
import time  # Для текущего времени
import os.path  # Для проверки существования файла

urlLeadAmo = '/api/v2/leads'

# Считывает ID автообзвона
fileDialout = open('dialoutid.txt', 'r')
dialoutid = int(fileDialout.read())
fileDialout.close()

# Открываем DB автообзвона
if os.path.isfile('DB_dialouts.json'):
    with open("DB_dialouts.json", "r") as dialoutsFile:
        leadsClear = json.load(dialoutsFile)
    dialoutsFile.close()

# Открываем файл с tokenCallApi
if os.path.isfile('tokenCallApi.json'):
    with open('tokenCallApi.json', 'r') as tokenCallApiFile:
        tokenCallApi = json.load(tokenCallApiFile)
    tokenCallApiFile.close()

# Открываем файл с loginUserAmo
if os.path.isfile('loginUserAmo.json'):
    with open('loginUserAmo.json', 'r') as loginUserAmoFile:
        loginUserAmo = json.load(loginUserAmoFile)
    loginUserAmoFile.close()

# Открываем файл с hashUserAmo
if os.path.isfile('hashUserAmo.json'):
    with open('hashUserAmo.json', 'r') as hashUserAmoFile:
        hashUserAmo = json.load(hashUserAmoFile)
    hashUserAmoFile.close()

# Открываем файл с tagLead
if os.path.isfile('tagLead.json'):
    with open('tagLead.json', 'r') as tagLeadFile:
        tagLead = json.load(tagLeadFile)
    tagLeadFile.close()

# Открываем файл с leadsStatusIdOk
if os.path.isfile('leadsStatusIdOk.json'):
    with open('leadsStatusIdOk.json', 'r') as leadsStatusIdOkFile:
        leadsStatusIdOk = json.load(leadsStatusIdOkFile)
    leadsStatusIdOkFile.close()

# Открываем файл с urlAmo
if os.path.isfile('urlAmo.json'):
    with open('urlAmo.json', 'r') as urlAmoFile:
        urlAmo = json.load(urlAmoFile)
    urlAmoFile.close()

urlGetDialOutStat = 'https://callapi.gravitel.ru/api/v1/getdialoutstat'
headers = {'Content-Type': 'application/json'}


jsonGetDialOutStat = {'token': tokenCallApi,
                      'dialoutid': dialoutid}

# Получаем статистику
getDialOutStat = requests.post(urlGetDialOutStat, headers=headers, json=jsonGetDialOutStat).json()
getDialOutStat = getDialOutStat['result']['data']

# Добавляем статус в БД
for i, elem in enumerate(getDialOutStat):
    for j, elem in enumerate(leadsClear):
        if getDialOutStat[i]['number'] == leadsClear[j]['main_contact']:
            leadsClear[j]['status'] = getDialOutStat[i]['intstatus']

#
# Проставляем Тэги если НЕДОЗВОН
#

# Connect with amoCRM POST
for i, elem in enumerate(leadsClear):

    # Ставим ТЭГ tagLead, если недозвон, то есть статус не 2
    if leadsClear[i]['status'] != 2:
        leadsClear[i]['count'] = leadsClear[i]['count'] - 1
        jsonUpdateLead = {'USER_LOGIN': loginUserAmo,
                          'USER_HASH': hashUserAmo,
                          'update':
                              [{'id': leadsClear[i]['id'],
                                'tags': tagLead,
                                'updated_at': time.time()}]}
        answerUpdateLeads = requests.post(urlAmo + urlLeadAmo, headers=headers, json=jsonUpdateLead).json()

    # Перекидываем сделку на другой этап (id = leadsStatusIdOk), если было 3 недозвона
    if leadsClear[i]['count'] == 0:
        jsonUpdateLead = {'USER_LOGIN': loginUserAmo,
                          'USER_HASH': hashUserAmo,
                          'update':
                              [{'id': leadsClear[i]['id'],
                                'status_id': leadsStatusIdOk,
                                'updated_at': time.time()}]}
        answerUpdateLeads = requests.post(urlAmo + urlLeadAmo, headers=headers, json=jsonUpdateLead).json()

# Убираем сделку, если count = 0 и если был дозвон
for i in reversed(range(len(leadsClear))):
    if leadsClear[i]['count'] == 0 or leadsClear[i]['status'] == 2:
        del leadsClear[i]

# Перезаписываем DB_dialouts
json.dump(leadsClear, open('DB_dialouts.json', 'w'))
