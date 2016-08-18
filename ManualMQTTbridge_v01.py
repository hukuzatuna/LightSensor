#!/usr/bin/python3
#######################################################################
# ManualMQTTbridge - Normal bridging between MQTT brokers assumes the
# data are compatible on both brokers. In some cases, the design of the
# topic has been ... not well thought out. As a result, extraneous data
# in the topic stream will interfere with normal bridging at the broker
# level. This program takes a topic stream that includes a sensor name
# (but not in the topic name) and translates it into a plain data stream
# for the remote broker.
#
# Author:     Philip R. Moyer
# Date:       August 2015
# Affiliatin: Adafruit Industries
#
# Credits:
#        Adafruit.IO examples         Tony DiCola
#
# Revision History:
#        version 01     Phil Moyer     Initial revision
#
#
# License: this code is in the public domain. It is released under the
# BSD license; any redistribution must include this header.
#######################################################################

#######################################################################
# Implementation Notes:
#        Hardware:
#                - NodeMCU ESP8266 Board. Can use any ESP8266, including
#                  Adafruit's ESP8266 Huzzah breakout (Product ID: 2471)
#                - Adafruit GA1A12S202 Log-scale Analog Light Sensor (Product
#                  ID: 1384)
#                - Adafruit half-size breadboard (Product ID: 64)
#                - Adafruit 2200 mAh LiPo battery pack (Product ID: 354)
#                - DuPont connectors (female to male)
#                - Voltage divider to reduce 3.3v signal from light sensor
#                  t0 1.0v analog pin signal
#                - Raspberry Pi 3 (Adafruit Product ID: 3055)
#
#        Software and Dependencies:
#                - io.adafruit.com account with one feed available
#                - Python3
#                - Adafruit_MQTT_Library
#
# Note: yes, yes, the right way to do this would have been to hook the
# sensor to the Raspberry Pi, then directly connect to io.adafruit.com.
# I, however, already had the ESP8266 set up with the sensor and programmed
# in Lua so I didn't want to change the hardware configuration. Also, I
# already had an MQTT broker running on my network, so there was no extra
# work involved in using it. This is NOT the way I would have build the
# system if I had originally intended it to interface with io.adafruit.com.
#######################################################################

########################
# Libraries
########################

import re
import string
import Adafruit_IO as AIO
import paho.mqtt.client as mqtt

########################
# Globals
########################

# Change these to match your local installation. Note: if you are (likely)
# running the MQTT broker on the same Raspberry Pi as this program, you will
# want to change localMQTTbroker to "localhost"
#
# Second Note: redact before doing a git push! :-)

localMQTTbroker = "CHANGE TO YOUR BROKER IP31"
localMQTTport = 1883
localMQTTuser = "CHANGE TO YOUR BROKER USER"
localMQTTpassword = "CHANGE TO YOUR BROKER PASSWORD"

remoteMQTTuser = "CHANGE TO YOUR ADAFRUIT.IO ID"
remoteMQTTpassword = "CHANGE TO YOUR ADAFRUIT.IO KEY"
remoteMQTTtopic = "lightsensor"

# You should not need to change anything below this line.

remoteMQTTbroker = "io.adafruit.com"
remoteMQTTport = 1883
messageCounter = 70                            # Keeps track of message count

########################
# Classes and Methods
########################


########################
# Functions
########################

# MQTT callbacks.

def AIOconnected(client):
	# Connected function will be called when the client is connected to Adafruit IO.
	return()

def AIOdisconnected(client):
	# Disconnected function will be called when the client disconnects.
	return()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("/sensors")

# The callback for when the program receives a message from the local topic.
# This is where the Good Stuff happens.
def on_message(client, userdata, msg):
	global messageCounter

	messageCounter = messageCounter + 1

	# Extract data value from local topic (last field)
	tmpStr = msg.payload.decode('ascii')
	values = tmpStr.split(' ')
	print(values)
	sensorName = values[0]
	sensorData = int(values[1])
	# If enough time has passed ...
	if (10 <= messageCounter):
		messageCounter = 0
		# Make connection to remote MQTT server...
		# Create an MQTT client instance.
		AIOclient = AIO.MQTTClient(remoteMQTTuser, remoteMQTTpassword)

		# Setup the callback functions defined above.
		AIOclient.on_connect    = AIOconnected
		AIOclient.on_disconnect = AIOdisconnected

		# Connect to the Adafruit IO server.
		AIOclient.connect()

		# Now the program needs to use a client loop function to ensure messages are
		# sent and received.  There are a few options for driving the message loop,
		# depending on what your program needs to do.
		AIOclient.loop_background()

		# Publish data element to remote server. This is a blind send - we don't
		# check return values. I know, bad style.
		print("Sending value %s to %s topic" % (sensorData, remoteMQTTtopic))
		AIOclient.publish(remoteMQTTtopic, sensorData)

		# Close down connection. A better way to do this would be to create
		# a class to hold the connection objects, which would allow us to leave
		# the io.adafruit.com connection open all the time. Version 02....
		AIOclient.disconnect()


########################
# Main
########################

if "__main__" == __name__:
	# Make connection to local MQTT server to extract data
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message

	# Not using passwords or encryption. Highly insecure on open nets!
	client.connect(localMQTTbroker, localMQTTport, 60)

	# Loop forever (remote connection handled in onMessage callback)
	client.loop_forever()

	# NOTREACHED.
	quit()
