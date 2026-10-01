# *---POUTLRY-GRID AI SYSTEM---*

*----------------------------------------------------------------------------*



#### *Overview:*



###### The Poultry-Grid AI system is a offline edge ai system that is used to monitor 5 environmental values, that is humidity, temperature, light\_intensity, ammonia levels,

###### and the ventilation rpm of the 12V-three wire fan with tachometer in the nursery

###### compartment of the Poultry-Grid poultry farming system. The ai achieved a:



\-Training Accuracy: 97.85%

\-Testing Accuracy: 97.35%



###### The AI classifies the nursery as Healthy, Warning or Critical. Ventilation has a large effect on gas build-up, humidity and temperature, so the fan runs at one of three speeds depending on the result.



Training Data: 80%

Testing Data: 20%



##### ***Inputs and outputs***

|***Input***|***Sensor***|***Notes***|
|-|-|-|
|HUMIDITY|DHT22|% RELATIVE HUMIDITY|
|GAS\_INDEX|MQ-135|% RELATIVE INDEX (0 = CLEAN-AIR BASELINE). NOT PPM OR AMMONIA SPECIFIC|
|TEMPERATURE|DHT22|CELCIUS|
|LIGHT|LDR ON LM393 BOARD|RELATIVE BRIGHTNESS|
|FAN\_RPM|FAN TACH WIRE|FROM A 3 WIRE 12V COMPUTER FAN|

##### 

The feature order is fixed everywhere: humidity, gas\_index, temperature, light, fan\_rpm.



|***OUTPUT***|***MEANING***|***FAN LEVEL***|
|-|-|-|
|0 HEALTHY|CONDITIONS ARE FINE|LOW|
|1 WARNING|SOMETHING IS DRIFTING|MEDIUM|
|2 CRITICAL|IMMEDIATE PROBLEM|HIGH|



The model is a small PyTorch network: 5 inputs → 16 → 16 → 3 classes.



##### ***Connections***<i>:</i>



|***PART***|***CONNECTIONS***|
|-|-|
|DHT22|GPIO 4|
|MQ-135 AND LDR|Through an ADS1115 ADC on I2C (channels 0 and 1)|
|FAN PWM|GPIO 18, through a MOSFET or fan driver on a separate 12 V supply|
|FAN TACH|GPIO 23, pulled up to 3.3 V|





##### THINGS NEEDED (SOLOMON TO YOU):

* DHT22	2	₵48.00 each	₵29.00 each
* MQ-135	2	₵35.00 each	₵35.00 each (28 in stock)
* LDR + LM393 module	1	₵14.00 for the 4-pin module	Not found
* 3-wire 12V fan	2–3 (your plan)	Not found	Only a 2-wire 40mm fan, ₵20.00


## License

MIT. See [LICENSE](LICENSE).
