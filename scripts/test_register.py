import http.cookiejar, urllib.request, urllib.parse, re

BASE = 'http://127.0.0.1:8000'
REGISTER = BASE + '/accounts/register/'

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# GET register page
req = urllib.request.Request(REGISTER, headers={'User-Agent': 'test-client'})
with opener.open(req, timeout=10) as r:
    page = r.read().decode('utf-8', errors='ignore')

m = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', page)
if not m:
    print('CSRF token not found on register page; aborting')
    raise SystemExit(1)

csrf = m.group(1)
print('Found CSRF token:', csrf)

# Prepare test user data
import uuid
u = 'testuser_' + uuid.uuid4().hex[:8]
email = f'{u}@example.local'
password = 'Testpass123!'

data = {
    'csrfmiddlewaretoken': csrf,
    'username': u,
    'email': email,
    'password1': password,
    'password2': password,
}
encoded = urllib.parse.urlencode(data).encode('utf-8')

# POST register form
post_req = urllib.request.Request(REGISTER, data=encoded, headers={
    'User-Agent': 'test-client',
    'Referer': REGISTER,
    'Content-Type': 'application/x-www-form-urlencoded',
})
with opener.open(post_req, timeout=10) as resp:
    final_url = resp.geturl()
    body = resp.read(2000).decode('utf-8', errors='ignore')

print('After POST, final URL:', final_url)

# Check if logged in by requesting homepage and looking for logout or username
home_req = urllib.request.Request(BASE + '/', headers={'User-Agent': 'test-client'})
with opener.open(home_req, timeout=10) as h:
    hbody = h.read(2000).decode('utf-8', errors='ignore')

if 'Logout' in hbody or u in hbody:
    print('Registration succeeded and user appears logged in as', u)
else:
    print('Registration may have failed; homepage snippet:')
    print(hbody[:1000])

# Also print cookies set
print('\nCookies:')
for c in cj:
    print(c.name, c.value)
