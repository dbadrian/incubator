  # behavior
  
  ## 0. Preheat Phase
  
 Empty fermentation box will be preheated to the first value given by the recipe. Once done, actual tracking is started by the user key press.
 Oven ambient temperature (tracked by ambient sensors) will be tracked. I would disregard humdity for now.
  
  ## 1 . Heating-Up
  Initially the inoculated medium will be at a lower temperature than ambient than entered (also ambient drops as well). Also the medium will not self-heat yet, thus the ambient temperature is good measure in the beginning and should be used to setpoint.
  
  ## 2. Food-Temp Tracking
  Once the medium reaches ambient temperature (setpoint defined in recipe), tracking will switch from ambient to food temperature.
  
  ## 3. Post-Tracking
  Should be defined in the cfg? Probably reducing temperature would make sense? Reduce humidity/and drying
  
