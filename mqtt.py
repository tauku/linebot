import subprocess
from subprocess import PIPE
import paho.mqtt.client as mqtt     
import datetime
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError


def send_line_msg(msg):
    
    line_bot_api = LineBotApi("your linebot api")
    line_bot_api.broadcast(TextSendMessage(text=msg))


def on_connect(client, userdata, flag, rc):
    print('[mqtt.py] Connected with result code ' + str(rc))  
    client.subscribe('pitest/button')   


def on_disconnect(client, userdata, flag, rc):
    if  rc != 0:
        print('[mqtt.py] Unexpected disconnection.')


def on_message(client, userdata, msg):
    
    get_msg = msg.payload.decode('utf-8')
    
    if get_msg == 'on':
        send_line_msg('motion_on')
        subprocess.run("sudo motion &", shell=True,)
        #print('[mqtt.py] Switching successed.')

    elif get_msg == 'off':
        send_line_msg('motion_off')
        subprocess.run("sudo pkill -f motion", shell=True,)
    
    elif get_msg == 'still':
        send_line_msg('still')
        
    elif get_msg == 'state':
        proc = subprocess.run("ps ax |grep -v grep |grep -o motion", shell=True,stdout=PIPE,stderr=PIPE, text=True)
        state = proc.stdout
    
        if  state in "motion":
            send_line_msg('motion is off')

        else :
            send_line_msg('motion is on')
    
    else :
        send_line_msg(get_msg)


client = mqtt.Client()                 
client.on_connect = on_connect         
client.on_disconnect = on_disconnect   
client.on_message = on_message         


client.username_pw_set("token:beebotte token") 
client.tls_set("/home/pi/linebot_mqtt/mqtt.beebotte.com.pem")
client.connect("mqtt.beebotte.com", 8883, 60)

send_line_msg('system_on')

client.loop_forever()                  