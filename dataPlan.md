______________________________________________________________________________________
|                           Data For Poultry Grid ML                                 |
-------------------------------------------------------------------------------------

1. Ammonia Levels
2. Temperature
3. Brightness
4. Moisture
5. Ventilation rate

    --------------------------AMMONIA LEVELS------------------------------

        |==>  Ammonia Levels For 1 Day Old Chicks <==|
Maximum ammonia level in a coop < 25ppm (parts per million).
Maximum ammonia level for a 1 day old chick < 10ppm (parts per million  ).
In the 20 ppm range, the ai is to flag a warning based on other factors, like if the ventilation rate is able to account for the increase in ammonia levels and the temperature and moisture levels are compensantiong for the ammonia level rise, since the environmental factors are connected.

Any level over 20-25 ppm can severely stunt growth, damage lungs and weaken immmne system.

        |==> Temperature Thresholds <==|
-Freezing Range: X < 10C
-Cold Range: 10C - 14C, must flag warning.
-Optimal Range: 15C - 24C(60F to 75F)
-Heat Stress Begins: 29C (85F), must flag warning.
-Danger Zone (Active cooling needed): Above 32C - 35C (90F - 95F), must flag warning
-Critical Limit: 38C (100F) and above (high risk of heat stroke), danger must be alerted.
     All these are dependent on other environmental factors, they compensate to reduce it. 

        |==> Brightness <==|
_ Normal Range 8lux - 10lux
_ Warning Range: 11lux < 30.9lux
_ Danger Range: >=31lux

Humidty:
-Normal Range: 50% - 70% RH
-Warning Range: 30% - 50% RH , or, 70% - 75% RH
-Danger Range: X > 75% RH, or, X < 30%

Ventilation Rate:
-Normal Range: 1 - 5 cubic feet per minute (CFM)
-Acceptable Rate For Compensation:      + If Temperature is above 32C, the ventilation rate must be increased by +2 CFM
                                        + If Temperature is below 14C, the ventilation rate must be decreased by 1/2 CFM
                                        + If Ammonia level is above 20ppm, the ventilation rate must be increased by +2 CFM
                                        + If humidity is less than 50% RH, the ventilation rate must be increased by +2 CFM
                                        + If humidity is above 70% RH, the ventilation rate must decreased by -2 CFM
                                        + If two or more concerning states occur at the same time, and there is to be increment
                                          of CFM it should be done once (just one plus 2, or, one -2, or one 1/2 depending on the states and combination of the current states) for the occuring states to compensate for the problem.
-Warning Range: 7 - 10 CFM, or , 0.9 - 0.5 CFM
-Danger Range: X > 10 CFM, or , X < 0.5 CFM
-5 CFM in hot weather.
