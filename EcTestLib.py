import paramiko
import os
import time
import re
import subprocess
import signal
import sys
import ConfigParser

configParser = ConfigParser.RawConfigParser()   
configFilePath = r'config.txt'
configParser.read(configFilePath)

status_check = configParser.get('TestConfig', 'status_check')
dut_ip = configParser.get('TestConfig', 'dut_ip')
board_name = configParser.get('TestConfig', 'board_name')

cros_sdk_path = configParser.get('ToolPath', 'cros_sdk_path')
abs_cros_sdk_path = configParser.get('ToolPath', 'abs_cros_sdk_path')

class EcTestLib(object):
		
	def run_command_on_dut(self, command, dut_ip):
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(dut_ip, username='root', password='test0000')
		stdin, stdout, stderr = client.exec_command(command)
		command_exit_status = stdout.channel.recv_exit_status()
		out= stdout.read()
		"""
		while not stdout.channel.exit_status_ready():
		    	# Only print data if there is data to read in the channel
		    	if stdout.channel.recv_ready():
				rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
				if len(rl) > 0:
			   		# Print data from stdout
			    		print stdout.channel.recv(1024),
		
			print "Command done."
		"""
		client.close()
		if command_exit_status == 0:
			return out
		else:
			return False	

	def copy_file_from_host_to_dut(self, src,dst, dut_ip):
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(dut_ip, username='root', password='test0000')

		sftp = client.open_sftp()
		sftp.put(src, dst)		
		sftp.close()

		if self.run_command_on_dut("ls -l " + dst, dut_ip):	
			print ("File copy successfull")	
			return True
		else:
			print ("File copy unsuccessfull")	
			return False


	def check_if_dut_is_live(self, dut_ip):
		hostname = dut_ip #example
		response = os.system("ping -c 1 " + hostname)

		#and then check the response...
		if response == 0:
			return True
		else:
			return False

	def wait_for_dut_to_come_back_on(self, minutes, dut_ip):
		minutes = int(minutes)
		t_end = time.time() + 60 * minutes
		while time.time() < t_end:
	    		if self.check_if_dut_is_live(dut_ip):
				return True
		return False



	def collect_dut_logs(self, dut_ip):
		if self.check_if_dut_is_live(dut_ip):
			if self.run_command_on_dut("ls -l /tmp/log*", dut_ip):
				print "Deleting existing generate_log file"
				self.run_command_on_dut("rm -rf /tmp/log*", dut_ip)
			print "Waiting for the logs to be generated"	
			generate_logs_output = self.run_command_on_dut("generate_logs", dut_ip)
			
			return generate_logs_output
		else:
			print "DUT %s is not up" % dut_ip
			return False
			

	def collect_logs_in_parallel(self, dut_ip, log_collection_folder):
		output = self.collect_dut_logs(dut_ip)
		if output:
			log_file_string = re.search('Log files are available at (.*)', output)
			if log_file_string:
				dut_log_file_path = log_file_string.group(1)	
				print dut_log_file_path
				return dut_log_file_path
			else:
				print "log file was not created successufully"
				return False
		else:
			return False

	def ec_console_test(self, ec_cmd, cros_sdk_path, outcome_string = ""):
		ec_uart_capture_enable_command = 'python' + ' ' + cros_sdk_path + ' ' + 'dut-control ec_uart_capture:on'
		ec_uart_capture_disable_command = 'python' + ' ' + cros_sdk_path + ' ' + 'dut-control ec_uart_capture:off'
		ec_console_system_status_command = 'python' + ' ' + cros_sdk_path + ' ' + 'dut-control ec_uart_cmd:' + ec_cmd
		ec_console_system_status_output = 'python' + ' ' + cros_sdk_path + ' ' + 'dut-control ec_uart_stream'
		os.system(ec_uart_capture_enable_command)
		os.system(ec_console_system_status_command)
		system_status_check = os.popen(ec_console_system_status_output).read()
		os.system(ec_uart_capture_disable_command)
		print (system_status_check)
		if outcome_string:
			#if system_status_check.find("outcome_string") != -1:
			if outcome_string.lower() in system_status_check.lower():
				return ec_cmd + " Test Result:  " +  "PASS"
			else: 
				return ec_cmd + " Test Result:  " + "FAIL"
		else:
			return ec_cmd + " output :" + system_status_check

	def run_ec_console_cmd(self, ec_cmd):
		ec_uart_capture_enable_command = 'python' + ' ' + abs_cros_sdk_path + ' ' + 'dut-control ec_uart_capture:on'
		ec_uart_capture_disable_command = 'python' + ' ' + abs_cros_sdk_path + ' ' + 'dut-control ec_uart_capture:off'
		ec_console_system_status_command = 'python' + ' ' + abs_cros_sdk_path + ' ' + 'dut-control ec_uart_cmd:' + ec_cmd
		ec_console_system_status_output = 'python' + ' ' + abs_cros_sdk_path + ' ' + 'dut-control ec_uart_stream'
		os.system(ec_uart_capture_enable_command)
		os.system(ec_console_system_status_command)
		system_status_check = os.popen(ec_console_system_status_output).read()
		os.system(ec_uart_capture_disable_command)
		system_status_check = re.sub('^ec_uart_stream:', '', system_status_check)
		print "==========================================================="
		print system_status_check
		print "==========================================================="
		#print ("%s console cmd output is: %s" %(ec_cmd, system_status_check))
		if system_status_check:
			return system_status_check
		else:
			return False

	#a function to check system status...we can keep adding check points for anything we want inside this function
	def status_check(self):
		mainfw_type = self.run_command_on_dut("crossystem mainfw_type", dut_ip)
		print mainfw_type
		if mainfw_type.find("developer") != -1:
			print "System is in Developer mode."
		else:
			print "System is in Normal mode"

		wifi_check = self.run_command_on_dut('/usr/sbin/lspci | grep -i "intel corporation wireless"', dut_ip)
		print wifi_check
		if wifi_check.find("Intel Corporation Wireless") != -1:
			print "Wifi detected successfully"
		else:
			print "Wifi detection failed. Exiting test."
			exit()
	


	def ec_test_file_input(self, fname):
		#read test file and store req, cmd and expected output and # values in a variable
		
		with open(fname) as f:
			content = f.readlines()
			content = (x.rstrip() for x in content)
			content = [content for content in content if content]
		
		if "cmd" in content:
			print
		for i in content:
			if "cmd" in i:
				ec_test_command = i.split(':')[1].lstrip()
			if "req" in i:
				req_number = i.split(':')[1].lstrip()

		print "ec test command is: %s" %(ec_test_command)
		print "req is: %s" %(req_number)
		print ""

		content = [content for content in content if "cmd" not in content]
		content = [content for content in content if "req" not in content]
		content = [content for content in content if "expect" not in content]
		
		for i in content:
			i = i.lstrip()
		content = [x.strip(' ') for x in content]
		print ("Expected is: %s" %(content))
			
		cmd_output = self.run_ec_console_cmd(ec_test_command)
		cmd_output = re.sub("\.+", "", cmd_output)
		cmd_output = re.sub(r'\\r\\n|\\r\\n\s+|\\r\\n\>', "|||", cmd_output)
		
		cmd_output = cmd_output.split("|||")
		#print type(cmd_output)		
		if ec_test_command in cmd_output[0]:
			del cmd_output[0]
		cmd_output = [x.strip(' ') for x in cmd_output]
		print ("Actual output: %s"%(cmd_output))
		for i in cmd_output:
			if re.match(r'\\n', i):
				print "it matches"
				print i
		


	def start_servod(self):
		#script_working_directory = os.getcwd()
		
		os.system("pgrep servod | xargs sudo kill -9")
		import subprocess
		p = subprocess.Popen('pgrep servod', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		retval = p.wait()
		out, err = p.communicate()

		if out:
			servod_pid = int(out.strip())
			print('servod Process found. Terminating it.')	
			os.kill(servod_pid, signal.SIGKILL)

		print('starting a fresh servod...')
		

		os.chdir(cros_sdk_path)	
		print os.getcwd()
		

		servod_cmd = 'python ' + abs_cros_sdk_path + ' ' + 'sudo ' + 'servod ' + '--board=' + board_name + ' ' + '&'
		os.system(servod_cmd)
		time.sleep(5)

		import subprocess
		output = subprocess.Popen(['pgrep', 'servod'], stdout=subprocess.PIPE).communicate()[0]

		if output:
			#print "Servod started successfully"
			return True
		else:
			#print "Servod couldn't start successfully. Exiting test."
			return False




