import urllib.request
import urllib.parse
import json
import sys

# Login
url_login = 'http://127.0.0.1:8000/api/v1/users/auth/login'
data = json.dumps({'username':'admin','password':'admin12345'}).encode('utf-8')
req = urllib.request.Request(url_login, data=data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode())
        token = res.get('access_token')
except Exception as e:
    print('Login error:', e)
    sys.exit(1)

# Search
# try to search something broader to catch any 500 errors across all students
url_search = 'http://127.0.0.1:8000/api/v1/admin/students/search?q=a'
req2 = urllib.request.Request(url_search, headers={'Authorization': f'Bearer {token}'})
try:
    with urllib.request.urlopen(req2) as response:
        print('Search a status:', response.status)
except urllib.error.HTTPError as e:
    print('Search a error:', e.code, e.read().decode())

url_search = 'http://127.0.0.1:8000/api/v1/admin/students/search?q=e'
req2 = urllib.request.Request(url_search, headers={'Authorization': f'Bearer {token}'})
try:
    with urllib.request.urlopen(req2) as response:
        print('Search e status:', response.status)
except urllib.error.HTTPError as e:
    print('Search e error:', e.code, e.read().decode())
