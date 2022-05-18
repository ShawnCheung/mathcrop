import sys
import base64
import requests
import json
import os
import time
import re


false = False
true = True
headers = { 'app_id':'',
            'app_key':'',
            'Content-type': 'application/json'}


filename = '../images/mixed_text_math.jpg'
savename = "./save.txt"


def uri(filename):
    image_uri = "data:image/jpg;base64," + base64.b64encode(open(filename, "rb").read()).decode()
    return image_uri


def pic2latex(filename, savename):
    image_uri = "data:image/jpg;base64," + base64.b64encode(open(filename, "rb").read()).decode()
    print("querying: ", filename)
    rrr = requests.post("https://api.mathpix.com/v3/text",
                  data = json.dumps({'src': image_uri}),
                  headers = headers)
    time.sleep(20)
    math = eval(json.dumps(json.loads(rrr.text), indent=4, sort_keys=True))["latex_styled"]
    print(math)
    f = open(savename, 'w')
    f.write(math)
    f.close()
    return math

def picbatch2latex(piclist, formulalistpath):
    formulalist = []
    data = {}
    urls = {}
    for pics in piclist:
        for pic in pics:
            urls[pic] = uri(pic)
    data['urls'] = urls
    # data['formats']=['latex_normal']
    data['callback'] = {'post': 'http://requestb.in/1ftatkr1'}
    print("querying batch server")
    r = requests.post("https://api.mathpix.com/v3/batch", 
            data=json.dumps(data),
            headers=headers,
            timeout=300)
    print("batch query succeed!")
    reply = json.loads(r.text)
    b = reply['batch_id']
    print("getting response")
    parse_response = requests.get("https://api.mathpix.com/v3/batch/" + b, headers=headers)
    print("get response succeed!")
    try:
        current = json.loads(parse_response.text)
        results = current['results']
        for i, pics in enumerate(piclist):
            form = []
            for j, pic in enumerate(pics):
                formpath = formulalistpath[i][j]
                math = results[pic]['latex']
                with open(formpath, 'w') as f:
                    f.write(math)
                form.append(math)
                print(formpath, ": ", math)
            formulalist.append(form)
    except:
        import pdb;pdb.set_trace()
        formulalist = formulalistpath
        print("detection failed!")
    return formulalist



def picbatch2latexv2(piclist, formulalistpath):
    formulalist = []
    data = {}
    urls = {}
    for pic in piclist:
        urls[pic] = uri(pic)
    data['urls'] = urls
    data['callback'] = {'post': 'http://requestb.in/1ftatkr1'}
    data['formats']=['latex_simplified']
    print("querying batch server")
    r = requests.post("https://api.mathpix.com/v3/batch", 
            json=data,
            headers=headers,
            timeout=300)
    print("batch query succeed!")
    # reply = json.loads(r.text)
    reply = r.json()
    b = reply['batch_id']
    print("getting response")
    parse_response = requests.get("https://api.mathpix.com/v3/batch/" + b, headers=headers)
    print("https://api.mathpix.com/v3/batch/" + b)
    time.sleep(2)
    print("get response succeed!")
    try:
        # print("in try")
        # import pdb;pdb.set_trace()
        current = json.loads(parse_response.text)
        results = current['results']
        for i, pic in enumerate(piclist):
            formpath = formulalistpath[i]
            if pic not in results.keys():
                math =  "not discovered!"
            else:
                math = results[pic]['latex_simplified']
                with open(formpath, 'w') as f:
                    f.write(math)
            print(formpath, ": ", math)
            formulalist.append(math)
    except:
        # print("in except")
        # import pdb;pdb.set_trace()
        formulalist = formulalistpath
        print("detection failed!")
    return formulalist
