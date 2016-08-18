
-- ###############################################################
-- lightsensor.lua - Uses standalone ESP8266 breakout (PID 2471)
-- board with GA1A12S202 Log-scale Analog Light Sensor (PID 1384),
-- both from Adafruit. It also uses a voltage divider to divide
-- 3.3v output to 0-1 volt for the 8266 analog-to-digital
-- converter, which can handle a max of 1 volt.

-- Phil Moyer
-- Adafruit

-- This code is open source, released under the BSD license. All
-- redistribution must include this header.
-- ###############################################################


-- ###############################################################
-- Global variables and parameters.
-- ###############################################################

localSSID = "CHANGEME"		-- the SSID of the WiFi network
localPass = "CHANGEME"		-- the WiFi password
sensorID = "light_001"		-- a sensor identifier for this device
tgtHost = "CHANGE TO BROKER IP31"	-- target host (broker)
tgtPort = 1883			-- target port (broker listening on)
mqttUserID = "CHANGEME"		-- account to use to log into the broker
mqttPass = "CHANGEME"		-- broker account password
mqttTimeOut = 120		-- connection timeout

-- Don't change anything below this line, please. -PRM

-- ###############################################################
-- Functions
-- ###############################################################

pubLight = function()
	rv = adc.read(0)				-- read light sensor
	pubValue = sensorID .. " " .. rv		-- build buffer
	mqttBroker:publish("/sensors", pubValue, 0, 0)	-- publish
	tmr.delay(3500000)				-- delay 3.5 seconds
end

reconn = function()
	-- reconnect to MQTT since we've gotten disconnected for some reason
	mqttBroker:connect(tgtHost, tgtPort, 0, function(client) print ("connected") end, function(client, reason) print("failed reason: "..reason) end)
end


-- ###############################################################
-- Set up WiFi configuration and make the connection.
-- ###############################################################

wifi.setmode(wifi.STATION)
wifi.sta.config(localSSID, localPass)
wifi.sta.connect()
tmr.delay(1000000) -- Wait a million uS = 1 second


-- ###############################################################
-- Establish connection to MQTT server.
-- ###############################################################

-- Instantiate an MQTT client object
mqttBroker = mqtt.Client(sensorID, mqttTimeOut, mqttUserID, mqttPass, 1)

-- Set up the event callbacks
mqttBroker:on("connect", function(client) print ("connected") end)
mqttBroker:on("offline", reconn)

mqttBroker:connect(tgtHost, tgtPort, 0, function(client) print ("connected") end, function(client, reason) print("failed reason: "..reason) end)


-- ###############################################################
-- Loop forever, maintain MQTT connection, publish data from sensor.
-- ###############################################################

-- Assumes the receiving system will add a timestamp
-- Call the publish light sensor value function
pubLight()

