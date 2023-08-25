#  project: fjscomm    issworld.py, merging world.html and simple.py     1/25/2023
#  issworld.py is the flask app that uses a stock world map that was hard to work with. 
#  plotly has great maps but I couldn't see how to get the realtime updates I have here.
## I'm going to redo this with a world map created by plotly.  planetA.py

from flask import Flask, jsonify, render_template, request, redirect, url_for
import datetime, json, requests
import os, subprocess, time, json

app = Flask(__name__)

def niceDate(ts):
    return datetime.datetime.utcfromtimestamp(ts).strftime('%H:%M:%S')

def cpu_util():
  cpu_util_cmd = "top -bn5 | head -3 | tail -1 | awk '{print 100-$8}'"
  dev = os.popen(cpu_util_cmd)
  cpu_util_raw = dev.read()
  return cpu_util_raw.strip()

def cpu_temp():
  dev = os.popen('/opt/vc/bin/vcgencmd measure_temp')
  cpu_temp_raw = dev.read()[5:-3]
  return cpu_temp_raw.strip()

def hostname():
  dev = os.popen("hostname")
  hn = dev.read()
  return hn.strip()

def mkdict(dtime):
    d = {}
    d["nicedate"] = dtime
    d["timestamp"] = dtime
    d['iss_position'] = {}
    d['iss_position']['longitude'] = '123'
    d['iss_position']['latitude'] = '456'
    d['utilization'] = cpu_util() + " %"
    d['temperature'] = cpu_temp()
    d['hostname'] = hostname()
    return d

@app.route('/')
def index():
    return redirect(url_for('refresh'))

# this returns json for simple.html to parse.   
@app.route("/issdata", methods=["GET"])
def issdata():
    dtime = datetime.datetime.now().strftime("%x %a %H:%M:%S.%f")
    # print("issdata route request at ", dtime)
    if  not True:
        # oj = json.dumps(mkdict(dtime))
        # print(oj, type(oj))   # <class 'str'>
        obj = requests.get("http://api.open-notify.org/iss-now.json")
        oj = obj.json()   # <class 'dict'> -- so I can add to it.
        oj["nicedate"] = niceDate(oj['timestamp'])
        oj['utilization'] = cpu_util() + " %"
        oj['temperature'] = cpu_temp()
        oj['hostname'] = hostname()
        return oj  # render_template("simple.html", oj=oj)
    else:
        # x = mkdict(dtime)
        #  {'nicedate': '01/24/23 ... 'iss_position': { ... 'latitude': '456'}}
        # oj = jsonify(x)
        #   <Response ... [200 OK]> <class 'flask.wrappers.Response'>
        obj = requests.get("http://api.open-notify.org/iss-now.json")
        oj = obj.json()   # <class 'dict'> -- so I can add to it.
        oj["nicedate"] = niceDate(oj['timestamp'])
        vhostname = hostname()
        oj['hostname'] = vhostname
        if vhostname != "HiMac2.local":
            oj['utilization'] = cpu_util() + " %"
            oj['temperature'] = cpu_temp()
        else:
            oj['utilization'] = "n/a on Mac"
            oj['temperature'] = "n/a on Mac"
        oj = jsonify(oj)
        oj.headers.add('Access-Control-Allow-Origin', '*')
        return oj

@app.route("/refresh", methods=["GET"])
def refresh():
    obj = requests.get("http://api.open-notify.org/iss-now.json")
    oj = obj.json()   # <class 'dict'> -- so I can add to it.
    oj["nicedate"] = niceDate(oj['timestamp'])
    print (oj['timestamp'])
    print (oj['nicedate'])
    print (oj['iss_position']['latitude'], oj['iss_position']['longitude'])
    return render_template("issworld.html", oj=oj)

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5089, debug=True)

# jsonify() vs json.dumps():  both take dict as argument
#   dumps() returns a JSON object, jsonify() returns a response
# https://flask.palletsprojects.com/en/2.1.x/patterns/javascript/

