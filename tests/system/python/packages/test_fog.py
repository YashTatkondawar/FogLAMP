import subprocess
import http.client
import json
import pytest
from collections import Counter
import os
import sys
import time

MAX_RETRIES = 2
SLEEP_FIX = 10
PI_TOKEN = "uid=8e639b38-4c23-4bde-9b0b-a2c8f0faafc9&crt=20190920064952172&sig=koQrTKtDaLPHbCAWiIUFB/avIYuFc1EdE3muaPE3AWA="
PI_IP = "10.2.5.23"

class TestClass:
    def setup_method(self,method):
        print ("*******Setting up***************\n")
        if os.path.exists("error.txt"):
            os.remove("error.txt")
        open("error.txt","w+")
        #subprocess.call(['./run'])
	
            
    
    def test_south_sinusoid(self,foglamp_url):
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "Sine","type": "south","plugin": "sinusoid","enabled": True,"config": {}}
        conn.request("POST", '/foglamp/service', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        
        for LOOP in range(MAX_RETRIES):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/south")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data["services"][0]["assets"][0]["asset"])            
            if "asset" in data["services"][0]["assets"][0]:              
              assert data["services"][0]["assets"][0]["asset"] == "sinusoid"
            elif LOOP < MAX_RETRIES :
              continue
            else :
              assert data["services"][0]["assets"][0]["asset"] == "sinusoid","TIMEOUT! sinusoid data not seen in South tab." + foglamp_url + "/foglamp/south" 
            
        print ("---- sinusoid data seen in South tab ----")
        
        
        for LOOP in range(MAX_RETRIES):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/asset")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0]["assetCode"])            
            if "assetCode" in data[0]:              
              assert data[0]["assetCode"] == "sinusoid"
            elif LOOP < MAX_RETRIES :
              continue
            else :
              assert data[0]["assetCode"] == "sinusoid","TIMEOUT! sinusoid data not seen in Asset tab." + foglamp_url + "/foglamp/asset" 
            
        print ("---- sinusoid data seen in Asset tab ----")
        
        for LOOP in range(MAX_RETRIES):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/ping")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)                        
            if "dataSent" in data:              
              assert data['dataSent'] != "" 
            elif LOOP < MAX_RETRIES :
              continue
            else :
              assert data['dataSent'] != "" ,"TIMEOUT! sinusoid data not seen in ping header." + foglamp_url + "/foglamp/ping" 
            
            
        print ("---- sinusoid data seen in ping header ----")
        
        
        for LOOP in range(MAX_RETRIES):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/asset/sinusoid?seconds=600")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0]["reading"]["sinusoid"])            
            if "sinusoid" in data[0]["reading"]:              
              assert data[0]["reading"]["sinusoid"] != ""
            elif LOOP < MAX_RETRIES :
              continue
            else :
              assert data[0]["reading"]["sinusoid"] != "" ,"TIMEOUT! sinusoid data not seen in sinusoid graph." + foglamp_url + "/foglamp/asset/sinusoid?seconds=600"
            
        print ("---- sinusoid data seen in sinusoid graph ----")
        
        print ("======================= SINUSOID SETUP COMPLETE =======================")
    
    #make this test conditional based on value of VERIFY_EGRESS_TO_PI        
    #TODO add the PI_TOKEN in producer token value and PI_IP
    #TODO change the name to PI Server
    def test_north_pi_egress(self,foglamp_url):
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "PI Server25","plugin": "PI_Server_V2","type": "north","schedule_repeat": 30,"schedule_type": "3","schedule_enabled": True,"config": {
          "URL": {"value": "https://"+PI_IP+":5460/ingress/messages"},"producerToken": {"value": PI_TOKEN},"compression": {"value": "false"}}}
        conn.request("POST", '/foglamp/scheduled/task', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        
        for LOOP in range(MAX_RETRIES):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/north")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0]["sent"])
            assert data[0]["sent"] != ""
            if "sent" in data[0]:              
              assert data[0]["sent"] != ""
            elif LOOP < MAX_RETRIES :
              continue
            else :
              assert data[0]["sent"] != "" ,"TIMEOUT! PI data sent not seen in North tab." + foglamp_url + "/foglamp/north" 
            
        print ("---- PI data sent seen in North tab ----")
        
        
        for LOOP in range(MAX_RETRIES):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/ping")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data["dataSent"])
            assert data['dataSent'] != ""
            if "dataSent" in data:              
              assert data['dataSent'] != "" 
            elif LOOP < MAX_RETRIES :
              continue
            else :
              assert data['dataSent'] != "" ,"TIMEOUT! sinusoid data not seen in ping header." + foglamp_url + "/foglamp/ping" 
            
        print ("---- PI data sent seen in ping header ----")
        
        #TODO add the sleep value        
        for LOOP in range(MAX_RETRIES):
            time.sleep(SLEEP_FIX)
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/statistics/history?minutes=10")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)            
            if "PI Server25" in data["statistics"][0]:              
              assert data["statistics"][0]["PI Server25"] != ""
            elif LOOP < MAX_RETRIES :
              continue
            else :
              assert data["statistics"][0]["PI Server25"] != "","TIMEOUT! PI data sent not seen in sent graph. " + foglamp_url + "/foglamp/statistics/history?minutes=10"       
            
        print ("---- PI data sent seen in sent graph ----")
        
        print ("======================= PI SETUP COMPLETE =======================")
        
    def test_sinusoid_max_filter(self,foglamp_url):
         
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "Square","plugin": "expression","filter_config": {"name": "square","expression": "if(sinusoid>0,0.5,-0.5)","enable": "true"}}
        conn.request("POST", '/foglamp/filter', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
    
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"pipeline": ["Square"]}
        conn.request("PUT", '/foglamp/filter/Sine/pipeline?allow_duplicates=true&append_filter=true', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
         
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "Max2","plugin": "expression","filter_config": {"name": "max","expression": "max(sinusoid, square)","enable": "true"}}
        conn.request("POST", '/foglamp/filter', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
    
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"pipeline": ["Max2"]}
        conn.request("PUT", '/foglamp/filter/Sine/pipeline?allow_duplicates=true&append_filter=true', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        for LOOP in range(MAX_RETRIES):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/asset/sinusoid?seconds=600")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0])            
            if "square" in data[0]["reading"] and "max" in data[0]["reading"]:              
              assert data[0]["reading"]["square"] != ""
              assert data[0]["reading"]["max"] != ""
            elif LOOP < MAX_RETRIES :
              continue
            else :
              assert data[0]["reading"]["square"] != "","TIMEOUT! square and max data not seen in sinusoid graph."+ foglamp_url + "/asset/sinusoid?seconds=600" 
              assert data[0]["reading"]["max"] != "","TIMEOUT! square and max data not seen in sinusoid graph."+ foglamp_url + "/asset/sinusoid?seconds=600"
              
        print ("---- sinusoid data seen in South tab ----") 
        
        print ("======================= SINUSOID MAX FILTER COMPLETE =======================")   
    
    def test_randomwalk_south_filter(self,foglamp_url):
         
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "Random","type": "south","plugin": "randomwalk","enabled": True,"config": {}}
        conn.request("POST", '/foglamp/service', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        time.sleep(SLEEP_FIX)
         
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "Ema","plugin": "python35","filter_config": {"config": {"rate": 0.07},"enable": "true"}}
        conn.request("POST", '/foglamp/filter', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
    
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"pipeline": ["Ema"]}
        conn.request("PUT", '/foglamp/filter/Random/pipeline?allow_duplicates=true&append_filter=true', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
               
        url = foglamp_url + '/foglamp/category/Random_Ema/script/upload'
        script_path = 'script=@scripts/ema.py'
        upload_script = "curl -sX POST '{}' -F '{}'".format(url,script_path)
        exit_code = os.system(upload_script)
        assert exit_code == 0
        
        for LOOP in range(MAX_RETRIES):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/asset/randomwalk?seconds=600")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0])            
            if "randomwalk" in data[0]["reading"] and "ema" in data[0]["reading"]:              
              assert data[0]["reading"]["randomwalk"] != ""
              assert data[0]["reading"]["ema"] != ""
            elif LOOP < MAX_RETRIES :
              continue
            else :
              assert data[0]["reading"]["randomwalk"] != "","TIMEOUT! randomwalk and ema data not seen in randomwalk graph."+ foglamp_url + "/asset/randomwalk?seconds=600"  
              assert data[0]["reading"]["ema"] != "","TIMEOUT! randomwalk and ema data not seen in randomwalk graph."+ foglamp_url + "/asset/randomwalk?seconds=600" 
            
        print ("---- randomwalk and ema data seen in randomwalk graph ----") 
        
        # DELETE Randomwalk South
        conn = http.client.HTTPConnection(foglamp_url) 
        conn.request("DELETE", '/foglamp/service/Random')
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status,"ERROR! Failed to delete randomwalk service"        
        
        print ("======================= RANDOMWALK SETUP COMPLETE =======================")
        
    def test_randomwalk_south_filter(self,foglamp_url):
        
        print ("Add Randomwalk south service again ...")
         
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "Random1","type": "south","plugin": "randomwalk","enabled": True,"config": {"assetName": {"value": "randomwalk1"}}}
        conn.request("POST", '/foglamp/service', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        # need to wait for FogLAMP to be ready to accept python file
        time.sleep(SLEEP_FIX)
         
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "PF","plugin": "python35","filter_config": {"config": {"rate": 0.07},"enable": "true"}}
        conn.request("POST", '/foglamp/filter', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        # Apply PF to Random
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"pipeline": ["PF"]}
        conn.request("PUT", '/foglamp/filter/Random1/pipeline?allow_duplicates=true&append_filter=true', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        print("upload trendc script...") 
               
        url = foglamp_url + '/foglamp/category/Random1_PF/script/upload'
        script_path = 'script=@scripts/trendc.py'
        upload_script = "curl -sX POST '{}' -F '{}'".format(url,script_path)
        exit_code = os.system(upload_script)
        assert exit_code == 0
        
        for LOOP in range(MAX_RETRIES):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/asset/randomwalk1?seconds=600")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0])            
            if "randomwalk" in data[0]["reading"] and "ema_long" in data[0]["reading"]:              
              assert data[0]["reading"]["randomwalk"] != ""
              assert data[0]["reading"]["ema_long"] != ""
            elif LOOP < MAX_RETRIES :
              continue
            else :
              assert data[0]["reading"]["randomwalk"] != "","TIMEOUT! randomwalk1 and ema_long data not seen in randomwalk graph."+ foglamp_url + "/asset/randomwalk1?seconds=600"  
              assert data[0]["reading"]["ema_long"] != "","TIMEOUT! randomwalk1 and ema_long data not seen in randomwalk graph."+ foglamp_url + "/asset/randomwalk1?seconds=600" 
            
        print ("---- randomwalk and ema_long data seen in randomwalk1 graph ----")
        
        print("upload trendc script with modified content...") 
        
        # DELETE Randomwalk South
        conn = http.client.HTTPConnection(foglamp_url) 
        conn.request("DELETE", '/foglamp/service/Random')
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status,"ERROR! Failed to delete randomwalk service"        
        
        print ("======================= RANDOMWALK SETUP COMPLETE =======================")
    
    def teardown_method(self,method):
        print ("\n********Tearing down********")
        #subprocess.call(['./remove'])
