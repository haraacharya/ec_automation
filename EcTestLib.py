import paramiko
import os
import time
import re
import subprocess

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
			








