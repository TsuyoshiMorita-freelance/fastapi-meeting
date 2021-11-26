import streamlit as st
import datetime
import requests
import json
import pandas as pd
from typing import List

page = st.sidebar.selectbox('Choose your page', ['users', 'rooms', 'bookings'])
title_temp ="""
	<div style="background-color:#464e5f;padding:10px;border-radius:10px;margin:10px;">
	<h4 style="color:white;text-align:center;">{}</h1>
	<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;" >
	<h6>Author:{}</h6>
	<br/>
	<br/>	
	<p style="text-align:justify">{}</p>
	</div>
	"""

table_temp ="""
	<div style="background-color:#464e5f;padding:10px;border-radius:10px;margin:10px;">
	<h4 style="color:white;text-align:center;">{}</h1>
	<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;" >
	<h6>Author:{}</h6>
	<br/>
	<br/>	
	<p style="text-align:justify">{}</p>
	</div>
	"""

if page == 'users':
    st.title('ユーザー登録画面')
    st.write(title_temp.format('テスト1','テスト2','テスト3'),unsafe_allow_html=True)

    with st.form(key='user'):
        #user_id: int = random.randint(0,10)
        username: str = st.text_input('ユーザー名',max_chars=12)
        data = {
            #'user_id': user_id,
            'username': username        
        }
        submit_button = st.form_submit_button(label="ユーザー登録")

    if submit_button:
        st.write('## レスポンス結果')
        url = 'http://127.0.0.1:8000/users'
        res = requests.post(url,data = json.dumps(data))
        if res.status_code == 200:
            st.success('ユーザー登録完了')
        else:
            st.error('ユーザー登録失敗')
        st.json(res.json())
       
elif page == 'rooms':
    st.title('会議室登録画面')

    with st.form(key='room'):
        #room_id: int = random.randint(0,10)
        room_name: str = st.text_input('会議室名',max_chars=12)
        capacity: int = st.number_input('定員',step=1)
        data = {
            #'room_id': room_id,
            'room_name': room_name,
            'capacity': capacity        
        }
        submit_button = st.form_submit_button(label="会議室登録")

    if submit_button:
        url = 'http://127.0.0.1:8000/rooms'
        res = requests.post(url,data = json.dumps(data))
        if res.status_code == 200:
            st.success('会議室登録完了')
        else:
            st.error('会議室登録失敗')
        st.json(res.json())

elif page == 'bookings':
    st.title('会議室予約画面')

    url_users = 'http://127.0.0.1:8000/users'
    res = requests.get(url_users)
    users = res.json()
    users_name = {}
    for user in users:
        users_name[user['username']] = user['user_id']

    url_rooms = 'http://127.0.0.1:8000/rooms'
    res = requests.get(url_rooms)
    rooms = res.json()
    rooms_name = {}
    for room in rooms:
        rooms_name[room['room_name']] = {
            'room_id': room['room_id'],
            'capacity': room['capacity'],
        }

    st.write('### 会議室一覧')
    df_rooms = pd.DataFrame(rooms)
    df_rooms.columns = ['会議室名','定員', '会議室ID']
    st.table(df_rooms)


    url_bookings = 'http://127.0.0.1:8000/bookings'
    res = requests.get(url_bookings)
    bookings = res.json()
    df_bookings = pd.DataFrame(bookings)


    users_id = {}
    for user in users:
        users_id[user['user_id']] = user['username']
    rooms_id = {}
    for room in rooms:
        rooms_id[room['room_id']] = {
            'room_name': room['room_name'],
            'capacity': room['capacity']
        }

    to_username = lambda x: users_id[x]
    to_room_name = lambda x: rooms_id[x]['room_name']
    to_datetime = lambda x: datetime.datetime.fromisoformat(x).strftime('%Y/%m/%d %H:%M')

    booking_id = {}
    for booking in bookings:
        booking_id[booking['booking_id']] = {
            'booking_name': f'{booking["booking_id"]} {to_username(booking["user_id"])} {to_room_name(booking["room_id"])} {to_datetime(booking["start_datetime"])}'
        }


    if (df_bookings.empty == False):
        ## 削除フォーム
        with st.form(key='delete_booking'):
            booking_ids: List[int] = st.multiselect(
                "予約削除", booking_id.keys(), format_func=lambda x: booking_id[x]['booking_name']
            )
            submit_delete_button = st.form_submit_button(label="予約削除")

        ## 削除処理
        if submit_delete_button:
            st.write(booking_ids)
            data = {
                'booking_ids': booking_ids,
            }
            url = 'http://127.0.0.1:8000/bookings'
            res = requests.delete(url,data = json.dumps(data))
            if res.status_code == 200:
                st.success('指定した会議室の予約を削除致しました。')
            else:
                st.error('会議室の予約の削除に失敗致しました。')

        ## 予約一覧表示用処理
        df_bookings['user_id'] = df_bookings['user_id'].map(to_username)
        df_bookings['room_id'] = df_bookings['room_id'].map(to_room_name)
        df_bookings['start_datetime'] = df_bookings['start_datetime'].map(to_datetime)
        df_bookings['end_datetime'] = df_bookings['end_datetime'].map(to_datetime)

        df_bookings = df_bookings.rename(columns={
            'user_id': '予約者名',
            'room_id': '会議室名',
            'booked_num': '予約人数',
            'start_datetime': '開始時刻',
            'end_datetime': '終了時刻',
            'booking_id': '予約番号',
        })

        #df_bookings.columns = ['会議室名','定員', '会議室ID']
        st.write('### 予約一覧')
        st.table(df_bookings)

    with st.form(key='booking'):
        username: str = st.selectbox('予約者名', users_name.keys())
        room_name: str = st.selectbox('会議室名', rooms_name.keys())
        booked_num: int = st.number_input('予約人数', step=1,min_value=1)
        date = st.date_input('日付を入力', min_value=datetime.date.today())
        start_time = st.time_input('開始時刻： ', value=datetime.time(hour=9, minute=0))
        end_time = st.time_input('開始時刻： ', value=datetime.time(hour=20, minute=0))
        submit_button = st.form_submit_button(label="予約登録")

    if submit_button:
        user_id: int = users_name[username]
        room_id: int = rooms_name[room_name]['room_id']
        capacity: int = rooms_name[room_name]['capacity']

        data = {
            'user_id': user_id,
            'room_id': room_id,
            'booked_num': booked_num,
            'start_datetime': datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=start_time.hour,
                minute=start_time.minute
            ).isoformat(),
            'end_datetime': datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=end_time.hour,
                minute=end_time.minute
            ).isoformat(),
            'booked_num': booked_num,
        }

        if booked_num > capacity:
            st.error(f'{room_name}の定員は、{capacity}名です。{capacity}名以下の予約人数のみ受け付けています')
        elif start_time >= end_time:
            st.error('開始時刻が終了時刻を超えています')
        elif start_time < datetime.time(hour=9,minute=0, second=0) or end_time > datetime.time(hour=20,minute=0, second=0):
            st.error('利用時間は9:00から20:00となります。')
        else:
            st.write('## 送信データ')
            st.json(data)
            st.write('## レスポンス結果')
            url = 'http://127.0.0.1:8000/bookings'
            res = requests.post(url,data = json.dumps(data))
            if res.status_code == 200:
                st.success('会議室の予約が完了しました。')
            elif res.status_code == 404 and res.json()['detail'] == 'Alreday booked':
                st.error('指定の時間にはすでに予約が入っております。')
            else:
                st.error('会議室の予約が失敗しました。')

            st.write(res.status_code)
            st.json(res.json())
