import subprocess
import os
import sys
import time
import signal
from EcTestLib import EcTestLib
from datetime import datetime
import logging
import logging.handlers
import ConfigParser


LOG_FILENAME = datetime.now().strftime('ec_test_logfile_%H_%M_%d_%m_%Y.log')
LOG_FILENAME_STR = os.path.abspath(LOG_FILENAME)
print ("Log file name is: %s"% LOG_FILENAME)
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, )

#CONFIG PARAMETERS
configParser = ConfigParser.RawConfigParser()   
configFilePath = r'config.txt'
configParser.read(configFilePath)

status_chack = configParser.get('TestConfig', 'status_check')
dut_ip = configParser.get('TestConfig', 'dut_ip')
board_name = configParser.get('TestConfig', 'board_name')

cros_sdk_path = configParser.get('ToolPath', 'cros_sdk_path')
abs_cros_sdk_path = configParser.get('ToolPath', 'abs_cros_sdk_path')

#END CONFIG PARAMETERS

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
time.sleep(15)

import subprocess
output = subprocess.Popen(['pgrep', 'servod'], stdout=subprocess.PIPE).communicate()[0]

if output:
	print "Servod started successfully"
	logging.info("Servod started successfully")
else:
	print "Servod couldn't be started successfully. Exiting test."
	logging.error("Servod couldn't be started successfully. Exiting test.")
	exit()
#a function to check system status...we can keep adding check points for anything we want inside this function
def status_check():
	mainfw_type = test.run_command_on_dut("crossystem mainfw_type", dut_ip)
	print mainfw_type
	if mainfw_type.find("developer") != -1:
		print "System is in Developer mode."
		logging.info("System is in Developer mode.")
	else:
		print "System is in Normal mode"
		logging.info("System is in Normal mode.")

	wifi_check = test.run_command_on_dut('/usr/sbin/lspci | grep -i "intel corporation wireless"', dut_ip)
	print wifi_check
	if wifi_check.find("Intel Corporation Wireless") != -1:
		print "Wifi detected successfully"
		logging.info("Wifi detected successfully")
	else:
		print "Wifi detection failed. Exiting test."
		logging.error("Wifi detection failed. Exiting test.")
		exit()
	

if status_check:
	status_check()


print test.ec_console_test("i2cscan", abs_cros_sdk_path, 'Scanning 4 batt' )
print test.ec_console_test("powerinfo", abs_cros_sdk_path, 's0' )
print test.ec_console_test("flashinfo", abs_cros_sdk_path)
