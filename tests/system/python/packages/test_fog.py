import subprocess
import http.client
import json
import pytest
from collections import Counter
import os
import sys
import time

VERIFY_ENVIRO_PHAT=0

def setup_module(module):
    print ("*******Setting up***************\n")
    if os.path.exists("error.txt"):
        os.remove("error.txt")
    open("error.txt","w+")
    #subprocess.call(['./run'])

class TestSouth:
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
        
        
        for LOOP in range(retries):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/south")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data["services"][0]["assets"][0]["asset"])            
            if "asset" in data["services"][0]["assets"][0]:              
              assert data["services"][0]["assets"][0]["asset"] == "sinusoid"
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data["services"][0]["assets"][0]["asset"] == "sinusoid","TIMEOUT! sinusoid data not seen in South tab." + foglamp_url + "/foglamp/south" 
            
        print ("---- sinusoid data seen in South tab ----")
        
    def test_sinusoid_in_asset(self,foglamp_url):   
        for LOOP in range(retries):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/asset")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0]["assetCode"])            
            if "assetCode" in data[0]:              
              assert data[0]["assetCode"] == "sinusoid"
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data[0]["assetCode"] == "sinusoid","TIMEOUT! sinusoid data not seen in Asset tab." + foglamp_url + "/foglamp/asset" 
            
        print ("---- sinusoid data seen in Asset tab ----")
        
    def test_sinusoid_ping(self,foglamp_url):
        for LOOP in range(retries):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/ping")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)                        
            if "dataSent" in data:              
              assert data['dataSent'] != ""
              break 
            elif LOOP < retries - 1 :
              continue
            else :
              assert data['dataSent'] != "" ,"TIMEOUT! sinusoid data not seen in ping header." + foglamp_url + "/foglamp/ping" 
            
            
        print ("---- sinusoid data seen in ping header ----")
        
    def test_sinusoid_graph(self,foglamp_url):    
        for LOOP in range(retries):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/asset/sinusoid?seconds=600")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0]["reading"]["sinusoid"])            
            if "sinusoid" in data[0]["reading"]:              
              assert data[0]["reading"]["sinusoid"] != ""
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data[0]["reading"]["sinusoid"] != "" ,"TIMEOUT! sinusoid data not seen in sinusoid graph." + foglamp_url + "/foglamp/asset/sinusoid?seconds=600"
            
        print ("---- sinusoid data seen in sinusoid graph ----")
        
        print ("======================= SINUSOID SETUP COMPLETE =======================")

verify_egress_to_pi = 1 
@pytest.mark.skipif(verify_egress_to_pi == 0, reason="As mentioned in config file")    
class TestNorth:    
    def test_north_pi_egress(self,foglamp_url,pi_host,pi_port,pi_token):
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "PI Server27","plugin": "PI_Server_V2","type": "north","schedule_repeat": 30,"schedule_type": "3","schedule_enabled": True,"config": {
          "URL": {"value": "https://{}:{}/ingress/messages".format(pi_host,pi_port)},"producerToken": {"value": pi_token},"compression": {"value": "false"}}}
        conn.request("POST", '/foglamp/scheduled/task', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        for LOOP in range(retries):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/north")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0]["sent"])
            assert data[0]["sent"] != ""
            if "sent" in data[0]:              
              assert data[0]["sent"] != ""
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data[0]["sent"] != "" ,"TIMEOUT! PI data sent not seen in North tab." + foglamp_url + "/foglamp/north" 
            
        print ("---- PI data sent seen in North tab ----")
        
    def test_north_ping(self,foglamp_url):    
        for LOOP in range(retries):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/ping")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data["dataSent"])
            assert data['dataSent'] != ""
            if "dataSent" in data:              
              assert data['dataSent'] != ""
              break 
            elif LOOP < retries - 1 :
              continue
            else :
              assert data['dataSent'] != "" ,"TIMEOUT! sinusoid data not seen in ping header." + foglamp_url + "/foglamp/ping" 
            
        print ("---- PI data sent seen in ping header ----")
        
    def test_north_graph(self,foglamp_url):       
        for LOOP in range(retries):
            time.sleep(wait_time)
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/statistics/history?minutes=10")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)            
            if "PI Server" in data["statistics"][0]:              
              assert data["statistics"][0]["PI Server"] != ""
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data["statistics"][0]["PI Server"] != "","TIMEOUT! PI data sent not seen in sent graph. " + foglamp_url + "/foglamp/statistics/history?minutes=10"       
            
        print ("---- PI data sent seen in sent graph ----")
        
        print ("======================= PI SETUP COMPLETE =======================")
        
class TestSinusoidMaxSquare:    
    def test_sinusoid_square_filter(self,foglamp_url):
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
    
    def test_sinusoid_max_filter(self,foglamp_url):     
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
        
    def test_sinusoid_max_square(self,foglamp_url):
        for LOOP in range(retries):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/asset/sinusoid?seconds=600")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0])            
            if "square" in data[0]["reading"] and "max" in data[0]["reading"]:              
              assert data[0]["reading"]["square"] != ""
              assert data[0]["reading"]["max"] != ""
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data[0]["reading"]["square"] != "","TIMEOUT! square and max data not seen in sinusoid graph."+ foglamp_url + "/foglamp/asset/sinusoid?seconds=600" 
              assert data[0]["reading"]["max"] != "","TIMEOUT! square and max data not seen in sinusoid graph."+ foglamp_url + "/foglamp/asset/sinusoid?seconds=600"
              
        print ("---- sinusoid data seen in South tab ----") 
        
        print ("======================= SINUSOID MAX FILTER COMPLETE =======================")   
    
class TestRandomwalk:    
    def test_randomwalk_south(self,foglamp_url):         
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "Random","type": "south","plugin": "randomwalk","enabled": True,"config": {}}
        conn.request("POST", '/foglamp/service', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        time.sleep(wait_time)
     
    def test_python35(self,foglamp_url):     
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
        
    def test_randomwalk_python35(self,foglamp_url):    
        for LOOP in range(retries):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/asset/randomwalk?seconds=600")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0])            
            if "randomwalk" in data[0]["reading"] and "ema" in data[0]["reading"]:              
              assert data[0]["reading"]["randomwalk"] != ""
              assert data[0]["reading"]["ema"] != ""
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data[0]["reading"]["randomwalk"] != "","TIMEOUT! randomwalk and ema data not seen in randomwalk graph."+ foglamp_url + "/foglamp/asset/randomwalk?seconds=600"  
              assert data[0]["reading"]["ema"] != "","TIMEOUT! randomwalk and ema data not seen in randomwalk graph."+ foglamp_url + "/foglamp/asset/randomwalk?seconds=600" 
            
        print ("---- randomwalk and ema data seen in randomwalk graph ----") 
        
        # DELETE Randomwalk South
        conn = http.client.HTTPConnection(foglamp_url) 
        conn.request("DELETE", '/foglamp/service/Random')
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status,"ERROR! Failed to delete randomwalk service"        
        
        print ("======================= RANDOMWALK SETUP COMPLETE =======================")
        
class TestRandomwalk2:    
    def test_randomwalk2_south_filter(self,foglamp_url):        
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
        time.sleep(wait_time)
         
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
        
    def test_randomwalk2_python35_filter(self,foglamp_url):     
        for LOOP in range(retries):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/asset/randomwalk1?seconds=600")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0])            
            if "randomwalk" in data[0]["reading"] and "ema_long" in data[0]["reading"]:              
              assert data[0]["reading"]["randomwalk"] != ""
              assert data[0]["reading"]["ema_long"] != ""
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data[0]["reading"]["randomwalk"] != "","TIMEOUT! randomwalk1 and ema_long data not seen in randomwalk graph."+ foglamp_url + "/foglamp/asset/randomwalk1?seconds=600"  
              assert data[0]["reading"]["ema_long"] != "","TIMEOUT! randomwalk1 and ema_long data not seen in randomwalk graph."+ foglamp_url + "/foglamp/asset/randomwalk1?seconds=600" 
            
        print ("---- randomwalk and ema_long data seen in randomwalk1 graph ----")
        
        print("upload trendc script with modified content...")
        
        copy_file = "cp scripts/trendc.py scripts/trendc.py.bak"
        edit_file = "sed -i \"s/reading\[b'ema_long/reading\[b'ema_longX/g\" scripts/trendc.py"
        exit_code = os.system(copy_file)
        assert exit_code == 0
        exit_code = os.system(edit_file)
        assert exit_code == 0
        
        url = foglamp_url + '/foglamp/category/Random1_PF/script/upload'
        script_path = 'script=@scripts/trendc.py'
        upload_script = "curl -sX POST '{}' -F '{}'".format(url,script_path)
        exit_code = os.system(upload_script)
        assert exit_code == 0
        
    def test_updated_randomwalk2_python35_filter(self,foglamp_url):
        for LOOP in range(retries):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/asset/randomwalk1?seconds=600")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0])            
            if "randomwalk" in data[0]["reading"] and "ema_longX" in data[0]["reading"]:              
              assert data[0]["reading"]["randomwalk"] != ""
              assert data[0]["reading"]["ema_longX"] != ""
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data[0]["reading"]["randomwalk"] != "","TIMEOUT! randomwalk1 and ema_longX data not seen in randomwalk graph."+ foglamp_url + "/foglamp/asset/randomwalk1?seconds=600"  
              assert data[0]["reading"]["ema_longX"] != "","TIMEOUT! randomwalk1 and ema_longX data not seen in randomwalk graph."+ foglamp_url + "/foglamp/asset/randomwalk1?seconds=600" 
            
        print ("---- randomwalk and ema_longX data seen in randomwalk1 graph ----")
        
        move_file = "mv scripts/trendc.py.bak scripts/trendc.py"        
        exit_code = os.system(move_file)
        assert exit_code == 0
        
        url = foglamp_url + '/foglamp/category/Random1_PF/script/upload'
        script_path = 'script=@scripts/ema.py'
        upload_script = "curl -sX POST '{}' -F '{}'".format(url,script_path)
        exit_code = os.system(upload_script)
        assert exit_code == 0  
        
        for LOOP in range(retries):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/asset/randomwalk1?seconds=600")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0])            
            if "randomwalk" in data[0]["reading"] and "ema" in data[0]["reading"]:              
              assert data[0]["reading"]["randomwalk"] != ""
              assert data[0]["reading"]["ema"] != ""
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data[0]["reading"]["randomwalk"] != "","TIMEOUT! randomwalk and ema data not seen in randomwalk1 graph."+ foglamp_url + "/foglamp/asset/randomwalk1?seconds=600"  
              assert data[0]["reading"]["ema"] != "","TIMEOUT! randomwalk and ema data not seen in randomwalk graph."+ foglamp_url + "/foglamp/asset/randomwalk1?seconds=600" 
            
        print ("---- randomwalk and ema data seen in randomwalk graph ----")  
        
        print ("======================= RANDOMWALK SETUP 2 COMPLETE =======================")



#@pytest.mark.skipif($(cat /etc/os-release | grep -w ID | cut -f2 -d"=") != 'raspbian', reason="As mentioned in config file")
@pytest.mark.skipif(os.uname()[4][:3] == 'x86', reason="only compatible with x86 architecture")    
class TestEnviroPhat:
    def test_os():
      print(os.uname()[4][:3])
    
    
    def test_enviro_phat(self,foglamp_url): 
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "Enviro","type": "south","plugin": "envirophat","enabled": true,"config": {"assetNamePrefix": {"value": "e_"}}}
        conn.request("POST", '/foglamp/service', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
         
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "Fahrenheit","plugin": "expression","filter_config": {"name": "temp_fahr","expression": "temperature*1.8+32","enable": "true"}}
        conn.request("POST", '/foglamp/filter', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
    
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"pipeline": ["Fahrenheit"]}
        conn.request("PUT", '/foglamp/filter/Enviro/pipeline?allow_duplicates=true&append_filter=true', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        for LOOP in range(retries):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/asset/e_weather?seconds=600")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0])            
            if "temperature" in data[0]["reading"] and "max" in data[0]["reading"]:              
              assert data[0]["reading"]["temperature"] != ""
              assert data[0]["reading"]["temp_fahr"] != ""
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data[0]["reading"]["temperature"] != "","TIMEOUT! temperature and max data not seen in e_weather graph."+ foglamp_url + "/foglamp/asset/e_weather?seconds=600" 
              assert data[0]["reading"]["temp_fahr"] != "","TIMEOUT! square and temp_fahr data not seen in e_weather graph."+ foglamp_url + "/foglamp/asset/e_weather?seconds=600"
              
        print ("---- temperature and fahrenheit data seen in e_weather graph ----") 
        
        print ("======================= enviro-pHAT SETUP COMPLETE =======================")
        

class TestEventEngine:    
    # Enable Event Engine
    def test_event_engine(self,foglamp_url,retries):         
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "FogLAMP Notifications","type": "notification","enabled": True}
        conn.request("POST", '/foglamp/service', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data) 
        
        for LOOP in range(retries):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/service")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data)       
            for item in data["services"]:            
              if item['name'] == "FogLAMP Notifications": 
                    assert item['status'] == "running"
                    return              
              elif LOOP < retries - 1:                          
                    continue
              else :                   
                    assert item['status'] == "running","TIMEOUT! event engine is not running."+ foglamp_url + "/foglamp/service"
              
        print ("---- service reports event engine is running ----") 
        
        print ("======================= EVENT ENGINE ENABLED =======================")
    
class TestPositiveNegativeSineNotification:    
    # Add Notification with Threshold Rule and Asset Notification (Positive Sine)
    def test_positive_sine_notification(self,foglamp_url): 
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "Positive Sine","description": "Positive Sine notification instance","rule": "Threshold","channel": "asset","notification_type": "retriggered","enabled": True}
        conn.request("POST", '/foglamp/notification', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
       
    
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"asset": "sinusoid","datapoint": "sinusoid"}
        conn.request("PUT", '/foglamp/category/rulePositive%20Sine', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"asset": "positive_sine","description": "positive","enable": "true"}
        conn.request("PUT", '/foglamp/category/deliveryPositive%20Sine', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        for LOOP in range(retries):
            con=http.client.HTTPConnection(foglamp_url)
            con.request("GET", "/foglamp/asset/positive_sine?seconds=600")
            resp=con.getresponse()
            strdata=resp.read().decode()
            data=json.loads(strdata)
            #print (data[0])                     
            if "event" in data[0]["reading"] and "rule" in data[0]["reading"]:              
              assert data[0]["reading"]["event"] == "triggered"
              assert data[0]["reading"]["rule"] == "Positive Sine"
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data[0]["reading"]["event"] != "","TIMEOUT! positive_sine event not fired."+ foglamp_url + "/foglamp/asset/positive_sine?seconds=600" 
              assert data[0]["reading"]["rule"] != "","TIMEOUT! positive_sine event not fired."+ foglamp_url + "/foglamp/asset/positive_sine?seconds=600"
              
        print ("---- positive_sine event fired ----") 
        
        print ("======================= EVENT POSITIVE SINE COMPLETE =======================")
        
    def test_negative_sine_notification(self,foglamp_url,remove_data_file):
        remove_data_file("/tmp/out")
        
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "Negative Sine","description": "Negative Sine notification instance","rule": "Threshold","channel": "python35","notification_type": "retriggered","enabled": True}
        conn.request("POST", '/foglamp/notification', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        # Upload Python Script (write_out.py)
        url = foglamp_url + '/foglamp/category/deliveryNegative%20Sine/script/upload'
        script_path = 'script=@scripts/write_out.py'
        upload_script = "curl -sX POST '{}' -F '{}'".format(url,script_path)
        exit_code = os.system(upload_script)
        assert exit_code == 0  
    
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"asset": "sinusoid","datapoint": "sinusoid","condition": "<"}
        conn.request("PUT", '/foglamp/category/ruleNegative%20Sine', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"enable": "true"}
        conn.request("PUT", '/foglamp/category/deliveryNegative%20Sine', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        for LOOP in range(retries):
            if os.path.exists("/tmp/out"):
                break
            time.sleep(wait_time)
        
        if LOOP == retries - 1 :
            print ("TIMEOUT! negative_sine event not fired. No /tmp/out file.")
        else :
             print ("---- negative_sine event fired ----") 
        
        print ("======================= EVENT NEGATIVE SINE COMPLETE =======================")
    
class TestToggledEvent:    
    def test_event_toggled_sent_clear(self,foglamp_url):
        print ("Add sinusoid")
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name": "sin #1", "plugin": "sinusoid", "type": "south", "enabled":True}
        conn.request("POST", '/foglamp/service', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)                     
        assert data["id"] != "","ERROR! Failed to add sin #1"
        assert data["name"] != "","ERROR! Failed to add sin #1"
        
        #    echo "Add and enable Notification"
        print ("Create event instance with threshold and asset; with notification trigger type toggled")
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"name":"test","description":"test notification instance","rule":"Threshold","channel":"asset","notification_type":"toggled","enabled":True}
        conn.request("POST", '/foglamp/notification', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        print ("Set rule")
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"asset":"sinusoid", "datapoint":"sinusoid", "trigger_value": "0.8"}
        conn.request("PUT", '/foglamp/category/ruletest', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        print ("Set delivery")
        conn = http.client.HTTPConnection(foglamp_url)        
        data = {"asset": "sin0.8", "description":"asset notification", "enable":"true"}
        conn.request("PUT", '/foglamp/category/deliverytest', json.dumps(data))
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status
        res = res.read().decode()
        data = json.loads(res)
        print (data)
        
        
        print ("Sleeping for 20 seconds")
        time.sleep(20)
        
        print ("Verify sin0.8 has been created")
        con=http.client.HTTPConnection(foglamp_url)
        con.request("GET", "/foglamp/asset/sin0.8?seconds=600")
        resp=con.getresponse()
        strdata=resp.read().decode()
        data=json.loads(strdata)
        print (data)                     
            
        print ("When rule is triggred, There should be 2 entries in Logs->notifications NTFCL and NTFSN")
        con=http.client.HTTPConnection(foglamp_url)
        con.request("GET", "/foglamp/audit?limit=1&source=NTFSN&severity=INFORMATION")
        resp=con.getresponse()
        strdata=resp.read().decode()
        data=json.loads(strdata)
        print (data)
        con=http.client.HTTPConnection(foglamp_url)
        con.request("GET", "/foglamp/audit?limit=1&source=NTFCL&severity=INFORMATION")
        resp=con.getresponse()
        strdata=resp.read().decode()
        data=json.loads(strdata)
        print (data)
        
        print ("======================= TOGGLE EVENT NTFSN and NTFCL TEST COMPLETE =======================")
    
def teardown_module(module):
    print ("\n********Tearing down********")
    #subprocess.call(['./remove'])
