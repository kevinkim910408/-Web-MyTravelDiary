from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# mongoDB - pymongo, dnspython 패키지
from pymongo import MongoClient

# sparta@cluster0 (내 db폴더이름@내클러스터이름)
client = MongoClient('mongodb+srv://test:sparta@cluster0.m7jzf.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

from datetime import datetime

import requests
from bs4 import BeautifulSoup


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/diary', methods=['GET'])
def show_diary():
    contents = list(db.travel_diary.find({}, {'_id': False}));
    return jsonify({'contents': contents})


@app.route('/diary', methods=['POST'])
def save_diary():
    city_name_receive = request.form['city_name_give']
    my_review_receive= request.form['my_review_give']

    # file을 보낼 준비
    file = request.files["file_give"]
    extension = file.filename.split('.')[-1]

    # 현재시간을 가져오는 함수
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    uploaddate = today.strftime('%Y-%m-%d')

    # 파일의 이름은 file-현재시간을 붙힌다
    filename = f'file-{mytime}'

    # 파일의 경로
    save_to = f'static/{filename}.{extension}'

    # 내가 save_to 라는 파일을 저장할거다
    file.save(save_to)

    url = f'https://www.google.com/search?q={city_name_receive}'

    print(url)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    info = soup.select_one('#kp-wp-tab-overview > div.TzHB6b.cLjAic.LMRCfc > div > div > div > div > div > div:nth-child(1) > div > div > div > span').text

    doc = {
        'City_Name': city_name_receive,
        'Review': my_review_receive,
        'file': f'{filename}.{extension}',
        'time': f'{uploaddate}',
        'info':info,
        'url':url,
    }

    db.travel_diary.insert_one(doc)
    return jsonify({'msg': 'Saved'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)