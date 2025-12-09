import urllib.request
import sys
import time
url = 'http://127.0.0.1:8000/services/'
for i in range(10):
    try:
        resp = urllib.request.urlopen(url, timeout=5)
        content = resp.read(4096)
        print('STATUS:', resp.status)
        print('CONTENT-SNIPPET:')
        sys.stdout.buffer.write(content)
        break
    except Exception as e:
        print('Attempt', i+1, 'failed:', e)
        time.sleep(0.5)
else:
    print('Failed to fetch /services/ after retries')
