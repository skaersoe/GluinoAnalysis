import json
import sqlite3
from operator import itemgetter, attrgetter
import datetime

timeout = 1*60.0
def index():
    s = ['''
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <title>GluinoAnalysis Monitor | Gluino.com</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <link rel="stylesheet" href="style.css" type="text/css" media="screen" title="no title" charset="utf-8">
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js" type="text/javascript" charset="utf-8"></script>
    <script src="monitor.js" type="text/javascript" charset="utf-8"></script>
	
    </head>

    <div style="position: relative; margin: 0px auto; width: 762px;">
    		<a href="http://gluino.com"><img id="monitor_02" src="images/monitor_02.png" width="762" height="66" alt="" /></a>

    		<div id="site_info">
    			<div >''']
    s.append('''%s''')
    				
    s.append('''
    			</div>
    		</div>
    		 <div id="workers">
    		''')

   
    conn, c = _dbcon()
    c.execute("select * from settings ORDER BY id desc  LIMIT 1")
    settings = c.fetchone()
    freetext = settings[1]
    
    
    s[1]  = "<div class='freetext'>" + str(freetext) + "</div><div class='totalcores_wrap'><span class='totalcores'>xxx</span><div class='totalcores_label'>cores</div></div>" 
    
    s.append('''
    </div>
    </div>
    </body>
    </html>
    ''')

    return ''.join(s)
    
def getWorkers():
    """docstring for getWorkers"""
    conn, c = _dbcon()
    
    c.execute('select * from connectedWorkers')
    workers = c.fetchall()
    workers.sort(key=itemgetter(6))# Sort by name
    
    coresall = 0
    
    workers_out = []
    for row in workers:
        timedelta, ct, hb = _check_if_dead(int(row[0]), row[9])
        # if timeelta > timeout:
        #     continue
        #     
        coresall += row[5]
        wid = row[0]
        c.execute('select * from activeJobs where wid=?', (wid, ))
        jobs = c.fetchall()
        if len(jobs) > 0:
            status = "busy_site"
            client = "client: " + jobs[0][3]
        else:
            status = "ready_site"
            client = ''

        workers_out.append([row[0], status, row[6], client, row[5], row[9], timedelta])
        
    return json.dumps(workers_out)
    
def _check_if_dead(wid, worker_heartbeat):
    """Check if a worker has died"""
    current_time = datetime.datetime.utcnow()
    heart_beat = datetime.datetime.strptime(worker_heartbeat, "%Y-%m-%d %H:%M:%S.%f")
    delta = current_time - heart_beat
    if delta.seconds > timeout and delta.seconds < 86000: # FIXME some weird delta bug around 24:00:00
        _remove_dead(wid)
    
    return delta.seconds, current_time, heart_beat
    
def _remove_dead(wid):
    """If a worker doesn't respond kill it and its jobs"""
    conn, c = _dbcon()
    c.execute('delete from connectedWorkers where id=?', (wid, ))
    c.execute('delete from activeJobs where wid=?', (wid, ))
    
    conn.commit()
    c.close()

def _dbcon():
    conn = sqlite3.connect('/var/webhosting/mdj/mdj/websites/monitor.gluino.com/gluinomonitor.sqlite')
    c = conn.cursor()
    return conn, c
    
def createDB():
    """docstring for createDB"""
    conn, c = _dbcon()
    c.execute('''CREATE  TABLE "main"."connectedWorkers" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "wid" TEXT, "mac" TEXT, "ip" TEXT, "port" INTEGER, "cores" INTEGER, "name" TEXT, "pid" INTEGER, "jobsprocessed" INTEGER, "heartbeat" TEXT,  "heartbeat_checked" TEXT)''')
    c.execute('''CREATE TABLE "main"."activeJobs" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "wid" INTEGER, "files" TEXT, "userip" TEXT)''')
    c.execute('''CREATE TABLE "main"."allJobs" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "wid" INTEGER, "files" TEXT, "userip" TEXT)''')
    c.execute('''CREATE TABLE "main"."settings" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "freetext" TEXT)''')
    
    conn.commit()
    c.close()
def onStart(req):
    """docstring for putConnection"""
    conn, c = _dbcon()
    
    inputj = json.loads(req.form.getfirst('json', ''))
    
    t = ('', inputj["worker_mac"], inputj["worker_ipaddress"], int(inputj["worker_port"]), int(inputj["worker_maxcores"]), inputj["worker_name"], inputj["worker_pid"], 0, inputj["heartbeat"], '',)
    c.execute('insert into connectedWorkers values (NULL,?,?,?,?,?,?,?,?,?,?)', t)
    conn.commit()
    wid = c.lastrowid
    
    c.close()
    return wid    

def onClose(req):
    """docstring for putConnection"""
    conn, c = _dbcon()
    inputj = json.loads(req.form.getfirst('json', ''))

    c.execute('delete from connectedWorkers where (mac=? and  pid=?) or id=?', (inputj["worker_mac"], inputj["worker_pid"], inputj["monitor_instance_id"], ))
    conn.commit()

    return str(inputj["monitor_instance_id"])
    
def onJob(req):
    """docstring for onConnection"""
    conn, c = _dbcon()
    inputj = json.loads(req.form.getfirst('json', ''))
    wid = inputj["monitor_instance_id"]
    c.execute("insert into allJobs values (NULL,?,?,?)", (wid, len(inputj['jobfiles']), inputj['userip'],))
    c.execute("insert into activeJobs values (NULL,?,?,?)", (wid, len(inputj['jobfiles']), inputj['userip'],))
    
    conn.commit()
    jid = c.lastrowid

    c.close()
    return jid
    
def endJob(req):
    """end of job"""
    conn, c = _dbcon()
    inputj = json.loads(req.form.getfirst('json', ''))
    wid = inputj["monitor_instance_id"]
    c.execute('UPDATE connectedWorkers SET jobsprocessed=? WHERE id= ?', (inputj["jobsprocessed"], wid,))
    c.execute('delete from activeJobs where id=?', (inputj["job_id"], ))
    
    conn.commit()
    c.close()

def onHeartbeat(req):
    """docstring for onHeartbeat"""
    conn, c = _dbcon()
    inputj = json.loads(req.form.getfirst('json', ''))
    wid = inputj["monitor_instance_id"]
    c.execute('UPDATE connectedWorkers SET heartbeat=? WHERE id= ?', (inputj["heartbeat"], wid,))
    
    conn.commit()
    c.close()
    
def addSettings(req):
    """docstring for addSettings"""
    conn, c = _dbcon()
    inputj = json.loads(req.form.getfirst('json', ''))
    c.execute('INSERT INTO settings VALUES (NULL, ?)', (inputj["freetext"],))
    
    conn.commit()
    c.close()