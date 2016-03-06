try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! This is probably because you need superuser privileges. You can achieve this by"
          " using 'sudo' to run your script")

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    print "waiting..."
    GPIO.wait_for_edge(17, GPIO.RISING)
    print "click detected!"

except KeyboardInterrupt:
    GPIO.cleanup
GPIO.cleanup

#x = raw_input("Hit Enter to exit");
#print(x);
