#!/usr/bin/env python
import cayenne.client, datetime, time, serial, logging

# Cayenne authentication info. This should be obtained from the Cayenne Dashboard.
MQTT_USERNAME  = "MY_USERNAME"
MQTT_PASSWORD  = "MY_PASSWORD"
MQTT_CLIENT_ID = "MY_CLIENT_ID"

# Default location of serial port on pre 3 Pi models
#SERIAL_PORT =  "/dev/ttyAMA0"

# Default location of serial port on Pi models 3 and Zero
SERIAL_PORT =   "/dev/ttyS0"

#This sets up the serial port specified above. baud rate is the bits per second timeout seconds
#port = serial.Serial(SERIAL_PORT, baudrate=2400, timeout=5)

#This sets up the serial port specified above. baud rate and WAITS for any cr/lf (new blob of data from picaxe)
port = serial.Serial(SERIAL_PORT, baudrate=2400)

client = cayenne.client.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, loglevel=logging.INFO)
#client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, loglevel=logging.DEBUG)
# For a secure connection use port 8883 when calling client.begin:
# client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, port=8883, loglevel=logging.INFO)

qos = 1
qos_good = 1
qos_bad = 1
timestamp = 1

while True:
  client.loop()
  try:
    rcv = port.readline() #read buffer until cr/lf
    #print("Serial Readline Data = " + rcv)
    rcv = rcv.rstrip("\r\n")
    synch,node,channel,data,cs = rcv.split(",")
    #print("rcv.split Data = : " + node + " " + channel + " " + data + " " + cs)
    #time.sleep(1)
    #Pacing delay to control rate of upload data

    checkSum = (int(node) + int(channel) + int(data))%256
    #checkSum = (checkSum)%256
    cs = int(cs)
    #print(checkSum,cs)

    time.sleep(.1)
    #Wait a bit for Serial Ports
    port.write(str(checkSum) + '\r\n')
    #Send something back from the Pi serial com port

    if checkSum == cs:
      qos_good = qos_good + 1
    else :
      qos_bad = qos_bad + 1
    #print(qos_good,qos_bad)

    if (time.time() > timestamp):
      qos = float(qos_good) / (qos_good + qos_bad)		#Calculate error rate ratio
      qos = round(qos,2) * 100					#Convert qos ratio to Percent
      #client.virtualWrite(24,qos_good,"analog_sesnor","null")
      client.virtualWrite(25,qos,"analog_sensor", "null")
      qos_good  = 1
      qos_bad   = 1
      timestamp = time.time() + 300 				#Every xxx seconds = 5 minutes

    if checkSum == int(cs) :
    #if cs = Check Sum is good then do the following
      if channel in ('1', '2', '3', '4', '17', '18', '19', '20', '23'):
        data = float(data)/10
        client.virtualWrite(int(channel), data, "analog_sensor", "null")

      elif channel in ('5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '21', '22', '24', '26', '30', '31', '32', '33'):
        data = float(data)/1
        client.virtualWrite(int(channel), data, "analog_sensor", "null")
      
      else:
        print("Unknown channel")
      
      # if channel == '25':
      #   data = float(data)/1
      #   client.virtualWrite(25, data, "analog_sensor", "null")

  except ValueError:
    qos_bad = qos_bad + 10
    #error = error + 10
    #error = float(error)/1
    #client.virtualWrite(22,error)/1
    #if Data Packet corrupt or malformed then...
    print("Data Packet corrupt or malformed")



