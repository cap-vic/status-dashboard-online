from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import base64
import json

app = Flask(__name__)

# Настройка Google Sheets
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# Вставь сюда строку из print(encoded)
ENCODED_KEY = """ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAic3RhdHVzLWRhc2hib2FyZC00NjgzMTMiLAogICJwcml2YXRlX2tleV9pZCI6ICIyY2Y1NjcyZTkyODQxMjY5MjcxZTJiYjI3NmMwYTM0NDk1ODVjZWQ3IiwKICAicHJpdmF0ZV9rZXkiOiAiLS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tXG5NSUlFdmdJQkFEQU5CZ2txaGtpRzl3MEJBUUVGQUFTQ0JLZ3dnZ1NrQWdFQUFvSUJBUUNXRlNOeGtMdTZZQkpUXG4vWDZEQUc5b2p3YVdKWVdBVmJZM3F1V0pXdUZ5VzZIS0RmRytteHZiR1UrTUg1R1MxWDZhUWFORm1WeDJHa3NkXG5xdXlqZVhGc3RubkQ1S3VuWEt3SkFHMWltUEdxdWE3Wi84clBFSGx5bndWUzVYY0ZVWCt6MS93U3p1emM2c3gzXG5rZ0lTUFB0NU8vZWcveGlRK0lHdjFhTm1xdkNIZFlmS0hWZDNFS2JXYTNxaFNyZFI4ZlFMTWhwekN5R2dsT0N1XG5aNVg1c2pPcDRlazkwTnozUklCYVlCY1hjbTdHRnV2dk4wWUV5TGFkZ3BTZmRSclZ4dFpoRlJVaXI1U3JpaW1ZXG5haVQ2Q1ZYc1N4ZmhsTE10Qm1BOGRyWkpCWjdDcG85ZXZVeElzRytsMzNwM1h6UFR6MDFkcG5WbHZIMTkyYUg4XG5VRFM0TDNxckFnTUJBQUVDZ2dFQUVLdUVabEY4ZmQrOGxCWlhVNnhjQ054cUQ0b0NEQlo1SGpISWtSQnhIaHlqXG5ieWYycnE4dEp1Ym16bHBBb2NpVGxBVmFZZTZvNEhnSExvMFUvN1lMZ29HNksxSUk1dXdFM1IzRHMwSG9XekxlXG5Bd1RGdldqSHRKTGVmOWltVEZ4RERQSWVqanJzVlpWc09la1QwSHdlMzlab3FPU1hacDErVDNqYitobGVqTGUyXG5XaHhTOXZCSWZIcVFVdUw2ZGlzQjY5cWFMTWt1MDZwZnJacDBWQ0xBQUZHZEtkSjZYY1NRYkxRVTcwMkRiRzFKXG5DRzlFTjRlQnM3Y25yODE1UDgzbjFRWWlaQjNuT0tyVVJJVk1mYkVjZ0ZBbmFzcnpkTzBWY01YNFRwQ3prYUtwXG5jdzlUK1FDaHk4UEFyMmdTYzRNUWJOWDY0RE5HYjRSVVJXOXRMcGZHTVFLQmdRREoxbnZoSFV5UWc5dG9SOVViXG5wcTJFdlB3OFNjRTE5VTN6TTlsem9Vb0N2MWNUMlphN0F1TFpkUGEwL3RRUXZyaFlhTGVVK2hTYTZ6NnBDa2FPXG53Nk9UcnNZM0tneENpWHlvemN3OGpvMU5QbWRacWVpWmVCdHBoL3FJeTMrYXY3TEpnOXRjZDFIWlljSnJ3bDFmXG4yeklLMXM5c3FsSEY0Y1NlM2xFcmJyaUU1UUtCZ1FDK1cwSklmbllDeWdialZsMmZlVWJxdHhBcXFWNjA4UEFiXG43TURCVHNHblh4cFFZZDhvY0xuMndOMnZXTXZaWm9KZmRvdWdOQmduTmtHTXdtbjl0bWI3eWRreEg0WURraXF1XG40bTNiTDI1enhrWHhGWVhhTEpCaG52V2lOTHl2Z0toL24xblMwK2RjMVp1ZmlRVTdpMEk1UlBHNW52N3FuMVpvXG5wTmRZVWhVWVR3S0JnRnFHdXBVaklQNElSZFlsc2Exdk9wQTRleUZISzBOYVBKWUNBVnZkVVdhZUR4NDJEMmJkXG5Tb1doOGkwSHhuR2tPT1plUVVpdVNhT2FNMFo1OTE5ODI5Y1hJb3dIYmV4QjRnbU1GRGhzNzI5ZnQ5YjlYL2ZGXG5hUFlTS1FwRnkzdksweE9TOGtZc3RpYzdzNG5GYVQvZS9qamlVN0kzU2Vubzh0a1dlVzF6Z1lzSkFvR0JBS2U3XG5ta2h1eG1YbXh2TURZelBtbFlxMURGWExNRnlZQWJ0WmZ1L1hDZVVGZEJab1owOG5KWFk4dEJxU1QrMmMyanhzXG5KTlJoa3ZiYVpDQTRIMVVrcU5JdEptaVdzbXZySEJsR0JDOGpPRnhqMWJWOWxaaU50QnVSQ2ppSDU4dHR2d3ZWXG55anh2NUdwMC90QXcySitETWpOc2dPTmpLcFJyR3FUU3U3NWpkWnNaQW9HQkFJMFpkREV5UEFFYXcwNjI4NEUrXG5LZVpHa2tsSzJheEkrak9yMzhodnpoS2xNTUNsMy9wMTNzSmJxb0lSODJQRjc3WjZuSGpuT2I0Yk9VMDVRR0JJXG5kTHovb044RFRwamVHbjZjUFZ0SGNnMGlTM3BteVB0ejJZVllOT1NUR3FCQTdiRzRPR3oydENEeTZVNlo5ckdKXG54aEJ5cWJ0WlpoK3VsUmtSbE5ZdisweXlcbi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS1cbiIsCiAgImNsaWVudF9lbWFpbCI6ICJzdGF0dXMtYm90QHN0YXR1cy1kYXNoYm9hcmQtNDY4MzEzLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAiY2xpZW50X2lkIjogIjExNzg5NDYxOTIyMDYzNTE0NzMyMSIsCiAgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi9hdXRoIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwKICAiYXV0aF9wcm92aWRlcl94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsCiAgImNsaWVudF94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3YxL21ldGFkYXRhL3g1MDkvc3RhdHVzLWJvdCU0MHN0YXR1cy1kYXNoYm9hcmQtNDY4MzEzLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAidW5pdmVyc2VfZG9tYWluIjogImdvb2dsZWFwaXMuY29tIgp9Cg=="""
key_data = json.loads(base64.b64decode(ENCODED_KEY).decode())
CREDS = ServiceAccountCredentials.from_json_keyfile_dict(key_data, SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET = CLIENT.open('Status Dashboard').sheet1

SURNAMES = [
    "Авдейкова Ольга", "Березина Екатерина", "Григорьева Лариса", "Гришкевич Вероника", "Данилов Антон",
    "Климов Сергей", "Кряжев Владимир", "Лапушкин Юрий", "Павлов Андрей", "Парижова Анна",
    "Петрова Мария", "Радько Ольга", "Садков Антон", "Тимаков Антон", "Черножуков Евгений",
    "Шкленский Станислав"
]

HOURS_24 = 24 * 60 * 60

def load_statuses():
    try:
        rows = SHEET.get_all_records()
        statuses = {}
        for row in rows:
            name = row.get('name')
            if name in SURNAMES:
                statuses[name] = {
                    'status': row.get('status', 'gray'),
                    'timestamp': float(row.get('timestamp', time.time()))
                }
        for name in SURNAMES:
            if name not in statuses:
                statuses[name] = {'status': 'gray', 'timestamp': time.time()}
        return statuses
    except Exception as e:
        print("Ошибка чтения:", e)
        return {name: {'status': 'gray', 'timestamp': time.time()} for name in SURNAMES}

def save_statuses(statuses):
    try:
        SHEET.clear()
        SHEET.append_row(['name', 'status', 'timestamp'])
        for name in SURNAMES:
            data = statuses.get(name, {'status': 'gray', 'timestamp': time.time()})
            SHEET.append_row([name, data['status'], str(data['timestamp'])])
    except Exception as e:
        print("Ошибка записи:", e)

@app.route('/')
def index():
    return render_template('index.html', surnames=SURNAMES)

@app.route('/status', methods=['GET'])
def get_status():
    statuses = load_statuses()
    now = time.time()
    updated = False
    for name, data in statuses.items():
        if now - data['timestamp'] > HOURS_24 and data['status'] != 'gray':
            data['status'] = 'gray'
            updated = True
    if updated:
        save_statuses(statuses)
    return jsonify({name: data['status'] for name, data in statuses.items()})

@app.route('/status', methods=['POST'])
def set_status():
    data = request.get_json()
    name = data.get('name')
    status = data.get('status')
    if not name or status not in ['green', 'red', 'gray'] or name not in SURNAMES:
        return jsonify({'error': 'Неверные данные'}), 400
    statuses = load_statuses()
    statuses[name] = {'status': status, 'timestamp': time.time()}
    save_statuses(statuses)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
