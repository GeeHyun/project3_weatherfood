from flask import Blueprint, render_template


def get_loc(do, si):
    do = '서울특별시'
    si = '종로구'
    return do, si



# 현재 날짜와 시간 가져오는 함수
def get_now():
    
    import datetime

    now = datetime.datetime.now()

    d = str(now.year) + str(now.month).zfill(2) + str(now.day)

    if now.minute > 30:
        t = str(now.hour).zfill(2) + '00'
    else:
        t = str(now.hour-1).zfill(2) + '30'

    return d, t



# mysql에서 location 테이블을 가져오는 함수
def get_location():
    import pymysql
    import pandas as pd

#    conn = pymysql.connect(host="us-cdbr-east-05.cleardb.net", port=3306, user='be3334bcb598f6', passwd='6da52b1b', db="heroku_425b0f678480ba1", charset='utf8')
    conn = pymysql.connect(host="localhost", port=3306, user='root', passwd='To8&beyond', db="project3", charset='utf8')
    cur = conn.cursor()

    cur.execute("SELECT * FROM location")
    data = cur.fetchall()

    location = pd.DataFrame(data, columns=['행정구역코드', '광역시도명', '시군구명', '격자x', '격자y'])

    return location



# 좌표 가져오는 함수
def get_grid(do, si):

    location = get_location()

    x = list(location[(location['광역시도명'] == do) & (location['시군구명'] == si)]['격자x'])[0]
    y = list(location[(location['광역시도명'] == do) & (location['시군구명'] == si)]['격자y'])[0]

    return x, y



# 날씨 api 가져오는 함수
# d: '20220624', t: '1800' (30분 단위로 갱신됨!)
def weatherapi(do, si):

    d, t = get_now()
    x, y = get_grid(do, si)

    import requests
    import json
    key = 'r+xdxqQDXqTHLozuYbT6G7pXG7Xw6xeKsqV96aabjddleLYYFS11oYQTWEFMyhshqFTj8jvkU37G7rKJlyzIXQ=='
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
    params ={'serviceKey' : key, 'pageNo' : '1', 'numOfRows' : '1000', 'dataType' : 'JSON', 'base_date' : d, 'base_time' : t, 'nx' : x, 'ny' : y }
    response = requests.get(url, params=params)
    data = json.loads(response.content)

    value_dict = {}
    for i in data['response']['body']['items']['item']:
        value_dict[i['category']] = i['obsrValue']

    return value_dict


# 현재 날씨 출력 및 피쳐 함수
def explain(do, si):

    value_dict = weatherapi(do, si)
    
    rain_snow_list = [0, 1, 2, 3, 1, 1, 2, 3]
    rain_snow_dict = {0:'특별할게 없는 오늘...',
                    1:'청 밖에 비가 내리는 오늘...',
                    2:'진눈개비가 내리는 오늘...',
                    3:'포근하게 눈이 내리는 오늘...'}



    text_list = [
        rain_snow_dict[rain_snow_list[int(value_dict['PTY'])]],
        f"온도...{value_dict['T1H']}도...",
        f"습도...{value_dict['REH']}%...",
        f"강수량...{value_dict['RN1']}...",
        f"풍속...{value_dict['WSD']}...",
        f"풍향...",
        "...",
        "이 온도... 이 습도... 그래, 그거야!"
        ]



    import datetime

    month = datetime.datetime.now().month
    hour = datetime.datetime.now().hour

    features = [month,
            hour,
            rain_snow_list[int(value_dict['PTY'])],
            float(value_dict['REH']),
            float(value_dict['RN1']),
            float(value_dict['T1H']),
            float(value_dict['WSD']),
            float(value_dict['VEC'])
            ]

    return text_list, features


# 모델에 값 넣는 함수
def to_model(features):

    import pickle
    
    model_dict = None
    with open('C:/Users/codnig/section3/project/model.pkl', 'rb') as pickle_file:
        model_dict = pickle.load(pickle_file)
    
    import pandas as pd
    X_test = pd.DataFrame([features])
    X_test.columns = ['월', '시간대', '강수/적설', '습도', '강수량', '기온', '풍속', '풍향i']

    recom_dict = {}
    for food in model_dict.keys():
        y_pred = model_dict[food].predict(X_test)
        y_pred_proba = model_dict[food].predict_proba(X_test)[:, 1]
        recom_dict[y_pred_proba[0]] = food
    
    result = recom_dict[max(recom_dict.keys())]

    return result
