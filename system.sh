lscpu 

echo temperature: 
vcgencmd measure_temp

echo cpu frequency
vcgencmd measure_clock arm
