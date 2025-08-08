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
ENCODED_KEY = """nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCWFSNxkLu6YBJT\n/X6DAG9ojwaWJYWAVbY3quWJWuFyW6HKDfG+mxvbGU+MH5GS1X6aQaNFmVx2Gksd\nquyjeXFstnnD5KunXKwJAG1imPGqua7Z/8rPEHlynwVS5XcFUX+z1/wSzuzc6sx3\nkgISPPt5O/eg/xiQ+IGv1aNmqvCHdYfKHVd3EKbWa3qhSrdR8fQLMhpzCyGglOCu\nZ5X5sjOp4ek90Nz3RIBaYBcXcm7GFuvvN0YEyLadgpSfdRrVxtZhFRUir5SriimY\naiT6CVXsSxfhlLMtBmA8drZJBZ7Cpo9evUxIsG+l33p3XzPTz01dpnVlvH192aH8\nUDS4L3qrAgMBAAECggEAEKuEZlF8fd+8lBZXU6xcCNxqD4oCDBZ5HjHIkRBxHhyj\nbyf2rq8tJubmzlpAociTlAVaYe6o4HgHLo0U/7YLgoG6K1II5uwE3R3Ds0HoWzLe\nAwTFvWjHtJLef9imTFxDDPIejjrsVZVsOekT0Hwe39ZoqOSXZp1+T3jb+hlejLe2\nWhxS9vBIfHqQUuL6disB69qaLMku06pfrZp0VCLAAFGdKdJ6XcSQbLQU702DbG1J\nCG9EN4eBs7cnr815P83n1QYiZB3nOKrURIVMfbEcgFAnasrzdO0VcMX4TpCzkaKp\ncw9T+QChy8PAr2gSc4MQbNX64DNGb4RURW9tLpfGMQKBgQDJ1nvhHUyQg9toR9Ub\npq2EvPw8ScE19U3zM9lzoUoCv1cT2Za7AuLZdPa0/tQQvrhYaLeU+hSa6z6pCkaO\nw6OTrsY3KgxCiXyozcw8jo1NPmdZqeiZeBtph/qIy3+av7LJg9tcd1HZYcJrwl1f\n2zIK1s9sqlHF4cSe3lErbriE5QKBgQC+W0JIfnYCygbjVl2feUbqtxAqqV608PAb\n7MDBTsGnXxpQYd8ocLn2wN2vWMvZZoJfdougNBgnNkGMwmn9tmb7ydkxH4YDkiqu\n4m3bL25zxkXxFYXaLJBhnvWiNLyvgKh/n1nS0+dc1ZufiQU7i0I5RPG5nv7qn1Zo\npNdYUhUYTwKBgFqGupUjIP4IRdYlsa1vOpA4eyFHK0NaPJYCAVvdUWaeDx42D2bd\nSoWh8i0HxnGkOOZeQUiuSaOaM0Z5919829cXIowHbexB4gmMFDhs729ft9b9X/fF\naPYSKQpFy3vK0xOS8kYstic7s4nFaT/e/jjiU7I3Seno8tkWeW1zgYsJAoGBAKe7\nmkhuxmXmxvMDYzPmlYq1DFXLMFyYAbtZfu/XCeUFdBZoZ08nJXY8tBqST+2c2jxs\nJNRhkvbaZCA4H1UkqNItJmiWsmvrHBlGBC8jOFxj1bV9lZiNtBuRCjiH58ttvwvV\nyjxv5Gp0/tAw2J+DMjNsgONjKpRrGqTSu75jdZsZAoGBAI0ZdDEyPAEaw06284E+\nKeZGkklK2axI+jOr38hvzhKlMMCl3/p13sJbqoIR82PF77Z6nHjnOb4bOU05QGBI\ndLz/oN8DTpjeGn6cPVtHcg0iS3pmyPtz2YVYNOSTGqBA7bG4OGz2tCDy6U6Z9rGJ\nxhByqbtZZh+ulRkRlNYv+0yy=="""
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