import http.cookiejar
import urllib.request
import urllib.parse
import re

BASE = 'http://127.0.0.1:8000'
LOGIN = BASE + '/accounts/login/'

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# GET login page
req = urllib.request.Request(LOGIN, headers={'User-Agent': 'test-client'})
with opener.open(req, timeout=10) as r:
    page = r.read().decode('utf-8', errors='ignore')

m = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', page)
if not m:
    print('CSRF token not found on login page; aborting')
    raise SystemExit(1)

csrf = m.group(1)
print('Found CSRF token:', csrf)

# Credentials for admin created earlier
username = 'admin'
password = 'AdminPass123!'

data = {
    'csrfmiddlewaretoken': csrf,
    'username': username,
    'password': password,
}
encoded = urllib.parse.urlencode(data).encode('utf-8')

post_req = urllib.request.Request(LOGIN, data=encoded, headers={
    'User-Agent': 'test-client',
    'Referer': LOGIN,
    'Content-Type': 'application/x-www-form-urlencoded',
})
with opener.open(post_req, timeout=10) as resp:
    final_url = resp.geturl()
    body = resp.read(2000).decode('utf-8', errors='ignore')

print('After POST, final URL:', final_url)

# Check homepage for login indicators
home_req = urllib.request.Request(BASE + '/', headers={'User-Agent': 'test-client'})
with opener.open(home_req, timeout=10) as h:
    hbody = h.read(2000).decode('utf-8', errors='ignore')

if 'Logout' in hbody or username in hbody:
    print('Login succeeded and user appears logged in as', username)
else:
    print('Login may have failed; homepage snippet:')
    print(hbody[:1000])

print('\nCookies:')
for c in cj:
    print(c.name, c.value)
