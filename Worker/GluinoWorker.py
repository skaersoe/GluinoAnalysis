#!/usr/bin/env python
# encoding: utf-8
"""
GluinoWorker.py

Created by Morten Dam Jørgensen on 2010-04-29.
Copyright (c) 2010 Niels Bohr Institute. All rights reserved.
"""

import sys
import os
import multiprocessing as mp
from multiprocessing.connection import Listener
import threading
from array import array
import tarfile
import shutil
import ConfigParser
from daemon import Daemon
import datetime
import time

# Required by MonitorClient
import ipinfo
import json
import urllib2
import urllib    
from socket import gethostname

class MonitorClient(object):
    """Connects to a monitor server and reports basic information"""
    def __init__(self, conn, worker):
        super(MonitorClient, self).__init__()
        
        # Gather information
        self.server = conn
        self.worker = worker
        
        # Generate UUID, one based on MAC address and one based on PID
        macs = ipinfo.getMACs()
        pid = os.getpid()

        
    def heartbeat(self):
        """Send a heartbeat signal to monitor once very x seconds"""
        while not self.stop_thread:
            j = json.dumps({"heartbeat" : datetime.datetime.utcnow().__str__(), "monitor_instance_id" : self.monitor_state_id})
            self.send(j, 'onHeartbeat')
            time.sleep(10)
            
    def onStart(self):
        """Starting Worker"""
        print "Sending connection infomation to %s" % self.server["address"]
        send_obj = {
            "worker_mac" : ipinfo.getMACs()[0].str, 
            "worker_pid" : os.getpid(),
            "worker_port" : self.worker.port,
            "worker_maxcores" : self.worker.maxcores,
            "worker_ipaddress" : self.worker.ipaddress,
            "worker_name" : self.worker.hostname,
            "heartbeat" : datetime.datetime.utcnow().__str__()
        }
        j = json.dumps(send_obj)
        
        self.monitor_state_id = self.send(j, "onStart")
        print "Monitor reports the id=%d for this worker" % int(self.monitor_state_id)
        
        ## Start heartbeat
        self.stop_thread = False
        self.heartbeat_thread = threading.Thread(target=self.heartbeat)
        self.heartbeat_thread.start()


    def onClose(self):
        """When Worker quits, tell the Monitor to signoff"""
        print "closing connection infomation to %s" % self.server["address"]
        self.stop_thread = True
        send_obj = {
            "monitor_instance_id" : self.monitor_state_id,
            "worker_mac" : ipinfo.getMACs()[0].str,
            "worker_pid" : os.getpid()
        }
        j = json.dumps(send_obj)
 
        self.send(j, "onClose")
        
    def onConnection(self):
        """On accepted connection with a Master, submit job information to GluinoMontor"""
        send_obj = {
            "monitor_instance_id" : self.monitor_state_id,
            "worker_mac" : ipinfo.getMACs()[0].str,
            "worker_pid" : os.getpid(),
            "jobfiles" : self.worker.jobs["input"],
            "userip" : self.worker.last_accepted[0]
            
        }
        j = json.dumps(send_obj)
        
        self.current_job_id =  self.send(j, "onJob")
        
    def onDisconnection(self):
        """Call on disconnection"""
        send_obj = {
            "worker_mac" : ipinfo.getMACs()[0].str, 
            "worker_pid" : os.getpid(),
            "jobsprocessed" : self.worker.jobsprocessed,
            "monitor_instance_id" : self.monitor_state_id,
            "job_id" : self.current_job_id
        }
        j = json.dumps(send_obj)
        
        self.send(j, "endJob")
        



    def send(self, jobj, subpage = ""):
        """Send a json object to the server"""
        baseurl = "http://%s:%d/" % (self.server["address"], self.server["port"])
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        # this creates a password manager
        passman.add_password(None, baseurl, self.server["username"], self.server["password"])

        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        # create the AuthHandler
        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)
        
        values = {'json' : jobj }
        data = urllib.urlencode(values)
        req = urllib2.Request(baseurl + subpage, data)
        response = urllib2.urlopen(req)
        return response.read()

class GluinoWorker(Daemon):
    """The GluinoWorker handles incomming requests and communication with the master"""
    def run(self):
        try:
            # Commandline override
            if len(sys.argv) > 2:
                if sys.argv[2][-3:] == "cfg":
                    options = sys.argv[1]
                else:
                    options = "WorkerSettings.cfg"
            else:
                options = "WorkerSettings.cfg"

            config = ConfigParser.ConfigParser()
            config.read(options)

            # Parse options file
            if config.has_section("settings"):
                self.ipaddress = config.get("settings", "ipaddress")
                self.port = config.getint("settings", "port")
                self.password = config.get("settings", "password")
                
                self.hostname = gethostname()
                if config.get("settings", "hostname"):
                    self.hostname = config.get("settings", "hostname")
                
                
                self.maxcores = mp.cpu_count()  
                if config.has_option("settings", "maxcores"):
                    if config.getint("settings","maxcores") < 0:
                        self.maxcores = mp.cpu_count() + config.getint("settings", "maxcores")
                    elif config.getint("settings", "maxcores") > 0 and config.getint("settings", "maxcores") <= self.maxcores:
                        self.maxcores = config.getint("settings", "maxcores")

            else:
                print "[WARNING] No input file detected, using default settings."    
                self.port = 1137
                self.ipaddress = ''
                self.password = 'glue balls'


            sys.path.append('workdir')
            from GluinoAnalysis.GluinoAnalysisWorker import GluinoAnalysisWorker


            address = (self.ipaddress, self.port)     # family is deduced to be 'AF_INET'
            listener = Listener(address, authkey=self.password)

            self.monitoring = False
            if config.has_section("monitor"): # Connect to service monitor
                if config.has_option("monitor", "address") and config.has_option("monitor", "username") and config.has_option("monitor", "password") and config.has_option("monitor", "port"):
                    monitor_con = {"address" : config.get("monitor", "address"), 
                        "port" : config.getint("monitor", "port"),
                        "username" : config.get("monitor", "username"),
                        "password" : config.get("monitor", "password")}
        
                    self.monitor = MonitorClient(monitor_con, self)
                    self.monitor.onStart()
                    self.monitoring = True
                    self.jobsprocessed = 0
                else:
                    print "External monitoring disabled"
                    self.monitoring = False

            printBanner(address, self.maxcores)
    
            while 1:
                print "[INFO] Listening on port %d..." % self.port
                try:
                    conn = listener.accept()

                    print 90*"-"
                    
                    self.last_accepted = listener.last_accepted
                    print '[INFO] Connection accepted from', listener.last_accepted

                    conn.send(["[INFO] '%s' Ready to compute (%d cores available)" % (self.ipaddress, self.maxcores), self.maxcores])

                    with open("job.tar.gz",'wb') as fin:
                        fin.write(conn.recv_bytes())
                    fin.close()

                    # extract file
                    tf = tarfile.open("job.tar.gz", 'r:gz')
                    tf.extractall("workdir")
                    tf.close()

                    conn.send(["[INFO] '%s' Files received and extracted..." % self.ipaddress])

                    _imp = __import__('userAnalysis', globals(), locals(), [], -1)      # Import file
                    reload(_imp)                    # Make sure the new userAnalysis is active


                    job = conn.recv()                # Receiving object (job[0] is the userAnalysis instance, and job[1] is configuration data (dict))
                    job[1]["maxcores"] = self.maxcores    # pass on the amount of cores to the jobhandler

                    print "[INFO] Number of inputfiles received: %d" % len(job[1]["input"])
                    if self.monitoring:
                        self.jobs = job[1]
                        self.monitor.onConnection() # Tell monitor
                
                    out = GluinoAnalysisWorker(job[0], job[1])  # Execute the job

                    conn.send([out.output])         # Return the histogram data (HistogramService obb)
                
                    if self.monitoring:
                        self.jobsprocessed += 1
                        self.monitor.onDisconnection()
                    
                    del out, job                    # FIXME might not be needed at all
                except EOFError:
                    print "[ERROR] Connection lost prematurely"
                except mp.AuthenticationError:
                    print "[ERROR] Authentication Error"
                finally:
                    try:
                        conn.close()
                    except:
                        pass # Already caught above...
                    # Clear directory
                    for fileName in os.listdir("workdir"):
                                if fileName not in ["GluinoAnalysis"]  and not fileName[0] == ".":
                                    try:
                                        os.remove("workdir/%s" % fileName)
                                    except OSError:
                                        try:
                                            shutil.rmtree("workdir/%s" % fileName)
                                        except:
                                            print "[ERROR] Error deleting file or directory: %s" % fileName
                    try:
                        os.remove("job.tar.gz")
                    except OSError:
                        print "[ERROR] Unable to remove job.tar.gz"

                    print 90*"-"
            listener.close()
        except KeyboardInterrupt:
            print "Closing down connections..."
        except:
            print "Exception"
            print sys.exc_info() # TODO Catch these instead
        finally:
            print "Closing down..."
            if self.monitoring:
                self.monitor.onClose()
        
def printBanner(addr = None, maxcores = mp.cpu_count()):
    """docstring for print"""
    print 90 *"="
    print
    print " Worker Node"
    print 
    print "\tGluinoAnalysis NTuple Analysis Framework\n\n"
    print "\tAuthor: Morten Dam Joergensen, 2010\n"
    print "\thttp://gluino.com"
    print
    print "\tLaunching on %s:%d" % addr
    print "\tUsing %d (of %d) cores" %  (maxcores, mp.cpu_count())
    print 90*"="
    


if __name__ == '__main__':
    # main()
    daemon = GluinoWorker('/tmp/gluinoWorker.pid')
    daemon.run()

    # if len(sys.argv) >= 2:
    #     if 'start' == sys.argv[1]:
    #         daemon.start()
    #     elif 'stop' == sys.argv[1]:
    #         daemon.stop()
    #     elif 'restart' == sys.argv[1]:
    #         daemon.restart()
    #     else:
    #         print "Unknow command"
    #         print "Allowed commands: start, stop, restart"
    #         sys.exit(2)
    #     sys.exit(0)
    # else:
    #     print "usage: %s start|stop|restart" % sys.argv[0]
    #     sys.exit(2)
    #     