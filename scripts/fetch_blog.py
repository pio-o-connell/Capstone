import urllib.request
resp = urllib.request.urlopen('http://127.0.0.1:8000/blog/')
print(resp.getcode())
print(resp.read(800).decode('utf-8', errors='ignore'))
