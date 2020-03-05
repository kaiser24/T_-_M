import requests
import json

#url = "http://127.0.0.1:5000/sad"

#r = requests.get(url)

#print( r.json())

# Ton to be sent
datas = {'video': '/home/pdi/Felipe_data/TnM_videos2process/test_format.avi',
        'poly':[
            {'x':237,'y':195},
            {'x':163,'y':404},
            {'x':666,'y':395},
            {'x':491,'y':163}
        ]
        
        }

#my file to be sent
local_file_to_send = 'tmpfile.txt'
with open(local_file_to_send, 'w') as f:
    f.write('I am a file\n')

url = "http://192.168.0.50:5000/getinfo"



files = {
    ('datas', ('datas', json.dumps(datas), 'application/json'))
}

r = requests.post(url, files=files)
print(str(r.content, 'utf-8')) 
'''
files = {
    'json': (None, json.dumps(datas), 'application/json')
} '''

