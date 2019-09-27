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
    
def make_post_connection(foglamp_url,post_url,data):
    conn = http.client.HTTPConnection(foglamp_url)
    conn.request("POST", post_url, json.dumps(data))
    res = conn.getresponse()
    print (res.status,res.reason)
    assert 200 == res.status
    res = res.read().decode()
    data = json.loads(res)
    print (data)
    return data
    
def make_get_connection(foglamp_url,get_url):
    con=http.client.HTTPConnection(foglamp_url)
    con.request("GET", get_url)
    resp=con.getresponse()
    strdata=resp.read().decode()
    data=json.loads(strdata)
    return data

def make_put_connection(foglamp_url,put_url,data):
    conn = http.client.HTTPConnection(foglamp_url)
    conn.request("PUT", put_url, json.dumps(data))
    res = conn.getresponse()
    print (res.status,res.reason)
    assert 200 == res.status
    res = res.read().decode()
    data = json.loads(res)
    print (data)
    
class TestSouth:
    def test_south_sinusoid(self,foglamp_url,retries,wait_time):
        data = {"name": "Sine","type": "south","plugin": "sinusoid","enabled": True,"config": {}}
        post_url = "/foglamp/service"
        make_post_connection(foglamp_url,post_url,data);
        
        time.sleep(wait_time * 2)
        
        for LOOP in range(retries):
            get_url = "/foglamp/south"
            data = make_get_connection(foglamp_url,get_url)            
            if "asset" in data["services"][0]["assets"][0]:
              assert data["services"][0]["assets"][0]["asset"] == "sinusoid"
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data["services"][0]["assets"][0]["asset"] == "sinusoid","TIMEOUT! sinusoid data not seen in South tab." + foglamp_url + "/foglamp/south" 
            
        print ("---- sinusoid data seen in South tab ----")
        
    def test_sinusoid_in_asset(self,foglamp_url,retries):   
        for LOOP in range(retries):
            get_url = "/foglamp/asset"
            data = make_get_connection(foglamp_url,get_url)           
            if "assetCode" in data[0]:              
              assert data[0]["assetCode"] == "sinusoid"
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data[0]["assetCode"] == "sinusoid","TIMEOUT! sinusoid data not seen in Asset tab." + foglamp_url + "/foglamp/asset" 
            
        print ("---- sinusoid data seen in Asset tab ----")
        
    def test_sinusoid_ping(self,foglamp_url,retries):
        for LOOP in range(retries):
            get_url = "/foglamp/ping"
            data = make_get_connection(foglamp_url,get_url)                        
            if "dataSent" in data:              
              assert data['dataSent'] != ""
              break 
            elif LOOP < retries - 1 :
              continue
            else :
              assert data['dataSent'] != "" ,"TIMEOUT! sinusoid data not seen in ping header." + foglamp_url + "/foglamp/ping" 
           
        print ("---- sinusoid data seen in ping header ----")
        
    def test_sinusoid_graph(self,foglamp_url,retries):    
        for LOOP in range(retries):
            get_url = "/foglamp/asset/sinusoid?seconds=600"
            data = make_get_connection(foglamp_url,get_url)            
            if "sinusoid" in data[0]["reading"]:              
              assert data[0]["reading"]["sinusoid"] != ""
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data[0]["reading"]["sinusoid"] != "" ,"TIMEOUT! sinusoid data not seen in sinusoid graph." + foglamp_url + "/foglamp/asset/sinusoid?seconds=600"
            
        print ("---- sinusoid data seen in sinusoid graph ----")
        
        print ("======================= SINUSOID SETUP COMPLETE =======================")

skip_verify_north_interface = 0 
@pytest.mark.skipif(skip_verify_north_interface == 0, reason="As mentioned in config file")    
class TestNorth:    
    def test_north_pi_egress(self,foglamp_url,pi_host,pi_port,pi_token,retries):
        data = {"name": "PI Server27","plugin": "PI_Server_V2","type": "north","schedule_repeat": 30,"schedule_type": "3","schedule_enabled": True,"config": {
          "URL": {"value": "https://{}:{}/ingress/messages".format(pi_host,pi_port)},"producerToken": {"value": pi_token},"compression": {"value": "false"}}}
        post_url = "/foglamp/scheduled/task"
        make_post_connection(foglamp_url,post_url,data);
        
        for LOOP in range(retries):
            get_url = "/foglamp/north"
            data = make_get_connection(foglamp_url,get_url) 
            assert data[0]["sent"] != ""
            if "sent" in data[0]:              
              assert data[0]["sent"] != ""
              break
            elif LOOP < retries - 1 :
              continue
            else :
              assert data[0]["sent"] != "" ,"TIMEOUT! PI data sent not seen in North tab." + foglamp_url + "/foglamp/north" 
            
        print ("---- PI data sent seen in North tab ----")
        
    def test_north_ping(self,foglamp_url,retries):    
        for LOOP in range(retries):
            get_url = "/foglamp/ping"
            data = make_get_connection(foglamp_url,get_url)
            if "dataSent" in data:              
              assert data['dataSent'] != ""
              break 
            elif LOOP < retries - 1 :
              continue
            else :
              assert data['dataSent'] != "" ,"TIMEOUT! sinusoid data not seen in ping header." + foglamp_url + "/foglamp/ping" 
            
        print ("---- PI data sent seen in ping header ----")
        
    def test_north_graph(self,foglamp_url,retries,wait_time):       
        for LOOP in range(retries):
            time.sleep(wait_time)
            get_url = "/foglamp/statistics/history?minutes=10"
            data = make_get_connection(foglamp_url,get_url)            
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
    def test_sinusoid_square_filter(self,foglamp_url,retries):
        data = {"name": "Square","plugin": "expression","filter_config": {"name": "square","expression": "if(sinusoid>0,0.5,-0.5)","enable": "true"}}
        post_url = "/foglamp/filter"
        make_post_connection(foglamp_url,post_url,data);
        
                
        data = {"pipeline": ["Square"]}
        put_url = "/foglamp/filter/Sine/pipeline?allow_duplicates=true&append_filter=true"
        make_put_connection(foglamp_url,put_url,data)
    
    def test_sinusoid_max_filter(self,foglamp_url,retries):  
        data = {"name": "Max2","plugin": "expression","filter_config": {"name": "max","expression": "max(sinusoid, square)","enable": "true"}}
        post_url = "/foglamp/filter"
        make_post_connection(foglamp_url,post_url,data);
      
                
        data = {"pipeline": ["Max2"]}
        put_url = "/foglamp/filter/Sine/pipeline?allow_duplicates=true&append_filter=true"
        make_put_connection(foglamp_url,put_url,data)
        
    def test_sinusoid_max_square(self,foglamp_url,retries,wait_time):
        time.sleep(wait_time)
        for LOOP in range(retries):
            get_url = "/foglamp/asset/sinusoid?seconds=600"
            data = make_get_connection(foglamp_url,get_url)            
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
    def test_randomwalk_south(self,foglamp_url,wait_time):    
        data = {"name": "Random","type": "south","plugin": "randomwalk","enabled": True,"config": {}}
        post_url = "/foglamp/service"
        make_post_connection(foglamp_url,post_url,data);
        
        time.sleep(wait_time)
     
    def test_python35(self,foglamp_url,wait_time):         
        data = {"name": "Ema","plugin": "python35","filter_config": {"config": {"rate": 0.07},"enable": "true"}}
        post_url = "/foglamp/filter"
        make_post_connection(foglamp_url,post_url,data);
               
        data = {"pipeline": ["Ema"]}
        put_url = "/foglamp/filter/Random/pipeline?allow_duplicates=true&append_filter=true"
        make_put_connection(foglamp_url,put_url,data)
               
        url = foglamp_url + '/foglamp/category/Random_Ema/script/upload'
        script_path = 'script=@scripts/ema.py'
        upload_script = "curl -sX POST '{}' -F '{}'".format(url,script_path)
        exit_code = os.system(upload_script)
        assert exit_code == 0
        
        time.sleep(wait_time)
    
    def test_randomwalk_python35(self,foglamp_url,retries):
        print ("asadsa",retries)
        #retries = 10    
        for LOOP in range(retries):
            print (LOOP)
            get_url = "/foglamp/asset/randomwalk?seconds=600"
            data = make_get_connection(foglamp_url,get_url)            
            if "randomwalk" in data[0]["reading"] and "ema" in data[0]["reading"]:              
                assert data[0]["reading"]["randomwalk"] != ""
                assert data[0]["reading"]["ema"] != ""
                print ("Found")
                break
            elif LOOP < retries - 1 :
                print ("Continue")
                continue
            else :
                assert data[0]["reading"]["randomwalk"] != "","TIMEOUT! randomwalk and ema data not seen in randomwalk graph."+ foglamp_url + "/foglamp/asset/randomwalk?seconds=600"  
                assert data[0]["reading"]["ema"] != "","TIMEOUT! randomwalk and ema data not seen in randomwalk graph."+ foglamp_url + "/foglamp/asset/randomwalk?seconds=600"
                print ("Not Found") 
            
        print ("---- randomwalk and ema data seen in randomwalk graph ----") 
        
        # DELETE Randomwalk South
        conn = http.client.HTTPConnection(foglamp_url) 
        conn.request("DELETE", '/foglamp/service/Random')
        res = conn.getresponse()
        print (res.status,res.reason)
        assert 200 == res.status,"ERROR! Failed to delete randomwalk service"        
        
        print ("======================= RANDOMWALK SETUP COMPLETE =======================")
        
class TestRandomwalk2:    
    def test_randomwalk2_south_filter(self,foglamp_url,wait_time,retries):        
        print ("Add Randomwalk south service again ...")      
        data = {"name": "Random1","type": "south","plugin": "randomwalk","enabled": True,"config": {"assetName": {"value": "randomwalk1"}}}
        post_url = "/foglamp/service"
        make_post_connection(foglamp_url,post_url,data);
        
        # need to wait for FogLAMP to be ready to accept python file
        time.sleep(wait_time)
         
            
        data = {"name": "PF","plugin": "python35","filter_config": {"config": {"rate": 0.07},"enable": "true"}}
        post_url = "/foglamp/filter"
        make_post_connection(foglamp_url,post_url,data);
        
        # Apply PF to Random
       
        data = {"pipeline": ["PF"]}
        put_url = "/foglamp/filter/Random1/pipeline?allow_duplicates=true&append_filter=true"
        make_put_connection(foglamp_url,put_url,data)
        
        print("upload trendc script...") 
               
        url = foglamp_url + '/foglamp/category/Random1_PF/script/upload'
        script_path = 'script=@scripts/trendc.py'
        upload_script = "curl -sX POST '{}' -F '{}'".format(url,script_path)
        exit_code = os.system(upload_script)
        assert exit_code == 0
        time.sleep(wait_time)
        
         
        for LOOP in range(retries):
            get_url = "/foglamp/asset/randomwalk1?seconds=600"
            data = make_get_connection(foglamp_url,get_url)             
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
     
    def test_randomwalk2_python35_filter(self,foglamp_url,retries,wait_time):   
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
        
        time.sleep(wait_time)
        
    
        for LOOP in range(retries):
            get_url = "/foglamp/asset/randomwalk1?seconds=600"
            data = make_get_connection(foglamp_url,get_url)            
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
    
    def test_updated_randomwalk2_python35_filter(self,foglamp_url,retries,wait_time):    
        move_file = "mv scripts/trendc.py.bak scripts/trendc.py"        
        exit_code = os.system(move_file)
        assert exit_code == 0
        
        url = foglamp_url + '/foglamp/category/Random1_PF/script/upload'
        script_path = 'script=@scripts/ema.py'
        upload_script = "curl -sX POST '{}' -F '{}'".format(url,script_path)
        exit_code = os.system(upload_script)
        assert exit_code == 0  
        
        time.sleep(wait_time)
        
        for LOOP in range(retries):
            get_url = "/foglamp/asset/randomwalk1?seconds=600"
            data = make_get_connection(foglamp_url,get_url)           
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


@pytest.mark.skipif(os.uname()[4][:3] == 'arm', reason="only compatible with arm architecture")    
class TestEnviroPhat:
    def test_enviro_phat(self,foglamp_url,retries,wait_time):
        data = {"name": "Enviro","type": "south","plugin": "envirophat","enabled": True,"config": {"assetNamePrefix": {"value": "e_"}}}
        post_url = "/foglamp/service"
        make_post_connection(foglamp_url,post_url,data);
         
               
        data = {"name": "Fahrenheit","plugin": "expression","filter_config": {"name": "temp_fahr","expression": "temperature*1.8+32","enable": "true"}}
        post_url = "/foglamp/filter"
        make_post_connection(foglamp_url,post_url,data);
        
        
        data = {"pipeline": ["Fahrenheit"]}
        put_url = "/foglamp/filter/Enviro/pipeline?allow_duplicates=true&append_filter=true"
        make_put_connection(foglamp_url,put_url,data)
        
        time.sleep(wait_time)
        
        for LOOP in range(retries):
            get_url = "/foglamp/asset/e_weather?seconds=600"
            data = make_get_connection(foglamp_url,get_url)            
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
        data = {"name": "FogLAMP Notifications","type": "notification","enabled": True}
        post_url = "/foglamp/service"
        make_post_connection(foglamp_url,post_url,data); 
        
        for LOOP in range(retries):
            get_url = "/foglamp/service"
            data = make_get_connection(foglamp_url,get_url)       
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
    def test_positive_sine_notification(self,foglamp_url,retries,wait_time):
        time.sleep(wait_time*2) 
        data = {"name": "Positive Sine","description": "Positive Sine notification instance","rule": "Threshold","channel": "asset","notification_type": "retriggered","enabled": True}
        post_url = "/foglamp/notification"
        make_post_connection(foglamp_url,post_url,data); 
       
        data = {"asset": "sinusoid","datapoint": "sinusoid"}
        put_url = "/foglamp/category/rulePositive%20Sine"
        make_put_connection(foglamp_url,put_url,data)
        
        data = {"asset": "positive_sine","description": "positive","enable": "true"}
        put_url = "/foglamp/category/deliveryPositive%20Sine"
        make_put_connection(foglamp_url,put_url,data)
        
        time.sleep(wait_time)
        
        for LOOP in range(retries):
            print (retries)
            print (LOOP)
            get_url = "/foglamp/asset/positive_sine?seconds=600"
            data = make_get_connection(foglamp_url,get_url)                     
            if "event" in data[0]["reading"] and "rule" in data[0]["reading"]:              
                assert data[0]["reading"]["event"] == "triggered"
                assert data[0]["reading"]["rule"] == "Positive Sine"
                break
            elif LOOP < retries - 1 :
                #print ("Continue")
                continue
            else :
                assert data[0]["reading"]["event"] != "","TIMEOUT! positive_sine event not fired."+ foglamp_url + "/foglamp/asset/positive_sine?seconds=600" 
                assert data[0]["reading"]["rule"] != "","TIMEOUT! positive_sine event not fired."+ foglamp_url + "/foglamp/asset/positive_sine?seconds=600"
                #print ("NotFound")
              
        print ("---- positive_sine event fired ----") 
        
        print ("======================= EVENT POSITIVE SINE COMPLETE =======================")
        
    def test_negative_sine_notification(self,foglamp_url,remove_data_file,retries,wait_time):
        remove_data_file("/tmp/out")
        
            
        data = {"name": "Negative Sine","description": "Negative Sine notification instance","rule": "Threshold","channel": "python35","notification_type": "retriggered","enabled": True}
        post_url = "/foglamp/notification"
        make_post_connection(foglamp_url,post_url,data); 
        
        # Upload Python Script (write_out.py)
        url = foglamp_url + '/foglamp/category/deliveryNegative%20Sine/script/upload'
        script_path = 'script=@scripts/write_out.py'
        upload_script = "curl -sX POST '{}' -F '{}'".format(url,script_path)
        exit_code = os.system(upload_script)
        assert exit_code == 0  
    
           
        data = {"asset": "sinusoid","datapoint": "sinusoid","condition": "<"}
        put_url = "/foglamp/category/ruleNegative%20Sine"
        make_put_connection(foglamp_url,put_url,data)
        
        
        data = {"enable": "true"}
        put_url = "/foglamp/category/deliveryNegative%20Sine"
        make_put_connection(foglamp_url,put_url,data)
        
        for LOOP in range(retries):
            if os.path.exists("/tmp/out"):
                break
            time.sleep(1)
        
        if LOOP == retries - 1 :
            print ("TIMEOUT! negative_sine event not fired. No /tmp/out file.")
        else :
             print ("---- negative_sine event fired ----") 
        
        print ("======================= EVENT NEGATIVE SINE COMPLETE =======================")
    
class TestToggledEvent:    
    def test_event_toggled_sent_clear(self,foglamp_url):
        print ("Add sinusoid")
        data = {"name": "sin #1", "plugin": "sinusoid", "type": "south", "enabled":True}
        post_url = "/foglamp/service"
        data = make_post_connection(foglamp_url,post_url,data);                      
        assert data["id"] != "","ERROR! Failed to add sin #1"
        assert data["name"] != "","ERROR! Failed to add sin #1"
        
        #    echo "Add and enable Notification"
        print ("Create event instance with threshold and asset; with notification trigger type toggled")
        data = {"name":"test","description":"test notification instance","rule":"Threshold","channel":"asset","notification_type":"toggled","enabled":True}
        post_url = "/foglamp/notification"
        make_post_connection(foglamp_url,post_url,data);                      
        
        print ("Set rule")
        data = {"asset":"sinusoid", "datapoint":"sinusoid", "trigger_value": "0.8"}
        put_url = "/foglamp/category/ruletest"
        make_put_connection(foglamp_url,put_url,data)
        
        print ("Set delivery")
        data = {"asset": "sin0.8", "description":"asset notification", "enable":"true"}
        put_url = "/foglamp/category/deliverytest"
        make_put_connection(foglamp_url,put_url,data)
        
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
        get_url = "/foglamp/audit?limit=1&source=NTFSN&severity=INFORMATION"
        data = make_get_connection(foglamp_url,get_url)
        print (data)
        
        get_url = "/foglamp/audit?limit=1&source=NTFCL&severity=INFORMATION"
        data = make_get_connection(foglamp_url,get_url)
        print (data)
        
        print ("======================= TOGGLE EVENT NTFSN and NTFCL TEST COMPLETE =======================")
    
def teardown_module(module):
    print ("\n********Tearing down********")
    #subprocess.call(['./remove'])
