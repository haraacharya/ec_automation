import subprocess
import os
import sys
import time
import signal
from EcTestLib import *
from datetime import datetime
import logging
import logging.handlers
import ConfigParser

 
LOG_DIR = datetime.now().strftime('ec_test_log_time_%H_%M_day_%d_%m_%Y')
LOG_FILENAME = datetime.now().strftime('ec_test_logfile_%H_%M_%d_%m_%Y.log')
LOG_FILENAME_STR = os.path.abspath(LOG_FILENAME)
print ("Log file name is: %s"% LOG_FILENAME)
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, )


test = EcTestLib()
script_working_directory = os.getcwd()
os.system("pgrep servod | xargs sudo kill -9")
p = subprocess.Popen('pgrep servod', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
retval = p.wait()
out, err = p.communicate()

if out:
	servod_pid = int(out.strip())
	print('servod Process found. Terminating it.')	
	os.kill(servod_pid, signal.SIGKILL)

print('starting a fresh servod...')
logging.info('starting a fresh servod...')

os.chdir(cros_sdk_path)	
print os.getcwd()
logging.info(os.getcwd())

servod_cmd = 'python ' + abs_cros_sdk_path + ' ' + 'sudo ' + 'servod ' + '--board=' + board_name + ' ' + '&'
os.system(servod_cmd)
time.sleep(5)

output = subprocess.Popen(['pgrep', 'servod'], stdout=subprocess.PIPE).communicate()[0]

if output:
	print "Servod started successfully"
	logging.info("Servod started successfully")
else:
	print "Servod couldn't start successfully. Exiting test."
	logging.error("Servod couldn't be started successfully. Exiting test.")
	#exit()


if status_check:
	test.status_check()

test.ec_test_file_input(script_working_directory + "/" + "8656_test.txt")





