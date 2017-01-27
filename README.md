ec automation
In Host machine run the below command to install paramiko module.
#sudo apt-get install python-ecdsa -y && wget http://ge.archive.ubuntu.com/ubuntu/pool/main/p/paramiko/python-paramiko_1.15.1-1_all.deb && sudo dpkg -i python-paramiko_1.15.1-1_all.deb
Go to any folder and clone the whole project as below.
#git clone https://github.com/haraacharya/ec_automation.git ec_automation
#cd ec_automation
Edit the config.txt with the right IP/board name Also edit the cros_sdk_path and absolute cros_sdk path based on the local host machine configuration.
Run the test as below.
#sudo python EcTest.py
(This will start the servod, and run the ecconsole tests.)
