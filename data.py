import requests
import json
import pandas as pd
import config as c
import traceback
from datetime import datetime

tokens = []
posts = [] 

for page in range(1, 51):
    
    payload = {"json_schema": {"category": {"value": c.category}, \
    "price": {"max": c.max_price,"min": c.min_price}, \
        "usage": {"max": c.max_usage,"min": c.min_usage}}, "last-post-date":c.last_post_date, "page":page}

    response = requests.post(url = c.url, json = payload)
    data = json.loads(response.content)

    tokens = tokens + ([widget['data']['token'] for widget in data['widget_list']])

missed = []
for token in tokens:

    url = f'https://api.divar.ir/v5/posts/{token}'
    response = requests.get(url)

    try:
        data = json.loads(response.content)
    except:
        with open('log.txt', 'a') as f:
            msg = str(datetime.today()) + traceback.format_exc() + '-'*60 + '\n'
            f.write(msg)
        missed.append(token)

    try:
        s = [{e['title']: e['value']} for e in data['widgets']['list_data'][0]['items']] + \
            [{e['title']: e['value']} for e in data['widgets']['list_data'][1:]]
        keys = [list(i.keys())[0] for i in s]
        values = [list(i.values())[0] for i in s]

        posts.append([token, dict(zip(keys,values)), data['widgets']['description']])
    
    except KeyError:
        with open('log.txt', 'a') as f:
            msg = str(datetime.today()) + traceback.format_exc() + '-'*40 + '\n'
            f.write(msg)
        missed.append(token)


df = pd.DataFrame(posts, columns = ['token', 'attributes', 'description'])
data = pd.concat([df.drop(['attributes'], axis=1), df['attributes'].apply(pd.Series)], axis=1)
data.to_csv('data.csv', index=False, mode='a')
