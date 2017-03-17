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

script_working_directory = os.getcwd()

#LOG_DIR = script_working_directory + "/" + datetime.now().strftime('log_folder_time_%H_%M_day_%d_%m_%Y')
#if not os.path.exists(LOG_DIR):
#        os.makedirs(LOG_DIR)

LOG_FILENAME = datetime.now().strftime('ec_test_hrs_%H_%M_day_%d_%m_%Y.log')
#LOG_FILENAME_STR = LOG_DIR + "/" + LOG_FILENAME
LOG_FILENAME_STR = LOG_FILENAME
print ("Log file name is: %s"% LOG_FILENAME_STR)
logging.basicConfig(filename=LOG_FILENAME_STR, level=logging.ERROR, )
#logging.basicConfig(filename=LOG_FILENAME_STR, level=logging.INFO, )
#logging.basicConfig(filename=LOG_FILENAME_STR, level=logging.DEBUG, )

test = EcTestLib()

if test.start_servod():
	print "servod started successfully"
	logging.info("servod started successfully")
else:
	print "servod failed to start. Exiting test."
	logging.info("servod failed to start. Exiting test.")
	exit()

if status_check:
	test.status_check()

test.non_blocking_run_command_on_dut("powerd_dbus_suspend", dut_ip)
print test.ec_console_test('powerinfo', abs_cros_sdk_path, outcome_string = "s3")





