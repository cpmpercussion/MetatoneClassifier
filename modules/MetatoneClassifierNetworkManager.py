import pybonjour
import OSC
import socket
import threading

METATONE_RECEIVING_PORT = 51200
CLASSIFIER_RECEIVING_PORT = 9000
CLASSIFIER_SERVICE_TYPE = "_osclogger._udp."

##
VISUALISER_MODE_ON = True
VISUALISER_PORT = 61200
VISUALISER_HOST = 'localhost'
##

class NetworkManager:

	def __init__(self):
		self.ip = ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1])
		#self.ip = ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][1:])

		self.name    = "MetatoneLiveProc"
		self.port    = CLASSIFIER_RECEIVING_PORT
		self.osc_sources = {}
		#self.receive_address = "10.0.1.2"
		try:
			self.receive_address = (self.ip[0], self.port)
		except IndexError:
			if (WEB_SERVER_MODE):
				self.receive_address = ("107.170.207.234",self.port)
			else:
				self.receive_address = ("localhost",self.port)

		self.client = OSC.OSCClient()
		# OSC Server. there are three different types of server. 
		self.server = OSC.OSCServer(self.receive_address) # basic
		##self.server = OSC.ThreadingOSCServer(receive_address) # threading
		##self.server = OSC.ForkingOSCServer(receive_address) # forking
		# Setup OSC Client.
		

		self.server.addMsgHandler("/metatone/touch", self.touch_handler)
		self.server.addMsgHandler("/metatone/touch/ended", self.touch_ended_handler)
		self.server.addMsgHandler("/metatone/switch", self.switch_handler)
		self.server.addMsgHandler("/metatone/online", self.onlineoffline_handler)
		self.server.addMsgHandler("/metatone/offline", self.onlineoffline_handler)
		self.server.addMsgHandler("/metatone/acceleration", self.accel_handler)
		self.server.addMsgHandler("/metatone/app",self.metatone_app_handler)

		# Bonjour Advertising
		self.bonjourService = pybonjour.DNSServiceRegister(name = self.name,
									 regtype = CLASSIFIER_SERVICE_TYPE,
									 port = self.port,
									 callBack = self.register_callback)

	##
	## Register the Bonjour service
	##
	def register_callback(sdRef, flags, errorCode, name, regtype, domain):
		if errorCode == pybonjour.kDNSServiceErr_NoError:
			print 'Registered service:'
			print '  name    =', name
			print '  regtype =', regtype
			print '  domain  =', domain

	def startOscServer():
		print("\nStarting OSCServer.")
		print("IP Address is: " + self.receive_address[0])
		global st 
		st = threading.Thread(target = self.server.serve_forever)
		st.start()

	def close_server():
		self.bonjourService.close()
		self.server.close()
		global st
		st.join()

	def send_gestures(classes):
		class_names = ['n','ft','st','fs','fsa','vss','bs','ss','c']
		for n in osc_sources.keys():
			if n in classes.keys():
				msg = OSC.OSCMessage("/metatone/classifier/gesture")
				msg.extend([n,class_names[classes[n]]])
				try:
					oscClient.sendto(msg,osc_sources[n])
				except OSC.OSCClientError:
					print("Couldn't send message to " + name + "removed from sources.")
					# logging.warning("Couldn't send message to " + name + "removed from sources.")
					remove_source(name)
				except socket.error:
					print("Couldn't send message to " + name + ", bad address. removed from sources.")
					remove_source(name)

	def send_touch_to_visualiser(touch_data):
		msg = OSC.OSCMessage("/metatone/touch")
		msg.extend(touch_data)
		try: 
			oscClient.sendto(msg,(VISUALISER_HOST,VISUALISER_PORT))
		except:
			msg = ""
			# print("Can't send messsages to visualiser.")

	def add_source_to_list(name,source):
		## Addressing a dictionary.
		global osc_sources
		source_address = (source[0],METATONE_RECEIVING_PORT)
		if (name not in osc_sources.keys()):
			osc_sources[name] = source_address

	def remove_source(name):
		global osc_sources
		if name in osc_sources: del osc_sources[name]

	def send_message_to_sources(msg):
		for name in osc_sources.keys():
			try:
				oscClient.sendto(msg,osc_sources[name])
				#print("Message sent to " + name)
			except OSC.OSCClientError:
				print("Couldn't send message to " + name)
				remove_source(name)
			except socket.error:
				print("Couldn't send message to " + name + ", bad address.")
				remove_source(name)
		log_line = [datetime.now().isoformat()]
		log_line.extend(msg)
		log_messages(log_line,live_messages)

	def get_device_name(device_id):
		if device_id in device_names:
			return device_names[device_id]
		else:
			return device_id

	def add_active_device(device_id):
		device_name = get_device_name(device_id)
		if device_name not in active_names:
			active_names.append(device_name)

	##
	## OSC Message Handling Functions
	##
	def touch_handler(addr, tags, stuff, source):
		add_source_to_list(get_device_name(stuff[0]),source)
		add_active_device(stuff[0])
		if (tags == "sfff"):
			time = datetime.now()
			message = [time.isoformat(),"touch",get_device_name(stuff[0]),stuff[1],stuff[2],stuff[3]]
			log_messages(message,live_messages)
			touch_messages.append([time,get_device_name(stuff[0]),stuff[1],stuff[2],stuff[3]])
			## Repeat Message to visualiser:
			if (VISUALISER_MODE_ON): 
				send_touch_to_visualiser(stuff)
			
	def touch_ended_handler(addr,tags,stuff,source):
		add_source_to_list(get_device_name(stuff[0]),source)
		add_active_device(stuff[0])
		if (tags == "s"):
			message = [datetime.now().isoformat(),"touch/ended",get_device_name(stuff[0])]
			log_messages(message,live_messages)

	def switch_handler(addr,tags,stuff,source):
		add_source_to_list(get_device_name(stuff[0]),source)
		add_active_device(stuff[0])
		if (tags == "sss"):
			message = [datetime.now().isoformat(),"switch",get_device_name(stuff[0]),stuff[1],stuff[2]]
			log_messages(message,live_messages)
			
	def onlineoffline_handler(addr,tags,stuff,source):
		add_source_to_list(get_device_name(stuff[0]),source)
		add_active_device(stuff[0])
		if (tags == "ss"):
			message = [datetime.now().isoformat(),addr,get_device_name(stuff[0]),stuff[1]]
			print(get_device_name(stuff[0]) + " is online with "+stuff[1]+".")
			log_messages(message,live_messages)
			
	def accel_handler(addr,tags,stuff,source):
		add_source_to_list(get_device_name(stuff[0]),source)
		add_active_device(stuff[0])
		if (tags == "sfff"):
			#do nothing
			message = [datetime.now().isoformat(),"accel",get_device_name(stuff[0]),stuff[1],stuff[2],stuff[3]]

	def metatone_app_handler(addr,tags,stuff,source):
		add_source_to_list(get_device_name(stuff[0]),source)
		add_active_device(stuff[0])
		if (tags == "sss"):
			message = [datetime.now().isoformat(),"metatone",get_device_name(stuff[0]),stuff[1],stuff[2]]
			log_messages(message,live_messages)
