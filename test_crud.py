import urllib.request, urllib.parse, urllib.error
from http.cookiejar import CookieJar
import re

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
urllib.request.install_opener(opener)

login_url = 'http://127.0.0.1:8000/uz/login/'
try:
    res = urllib.request.urlopen(login_url)
    html = res.read().decode('utf-8')
    match = re.search(r'name="csrfmiddlewaretoken" value="(.+?)"', html)
    if match:
        csrf_token = match.group(1)
        data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123', 'csrfmiddlewaretoken': csrf_token}).encode('utf-8')
        req = urllib.request.Request(login_url, data=data)
        res = urllib.request.urlopen(req)
        print('Login successful')
    else:
        print('CSRF token not found')
except Exception as e:
    print('Login failed:', e)

urls_to_test = [
    '/uz/article/create/',
    '/uz/journal/create/',
    '/uz/year/create/',
    '/uz/article/update/xizmat-korsatish-sohasini-modernizatsiya-qilish/42/',
    '/uz/article/delete/xizmat-korsatish-sohasini-modernizatsiya-qilish/42/'
]

for url in urls_to_test:
    try:
        res = urllib.request.urlopen('http://127.0.0.1:8000' + url)
        print(f'{url} GET status: {res.status}')
    except urllib.error.HTTPError as e:
        print(f'{url} GET error: {e.code}')
