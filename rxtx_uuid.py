import ggwave
import pyaudio
import messages_pb2
import random
import time
import uuid
import threading

id = uuid.uuid4()

p2 = pyaudio.PyAudio()

stream2 = p2.open(format=pyaudio.paFloat32, channels=1, rate=48000, input=True, frames_per_buffer=1024)

rxtxlist = []

class rxtx:
	
	def tx(self):
		while True:
			event_object.wait()
			txmessagelist = []
			z = 0
			while True:
				while rxtxlist:
					p1 = pyaudio.PyAudio()				
					waveform = ggwave.encode(rxtxlist[-1].SerializeToString().decode(), protocolId = 1, volume = 25)
					print('\nRetransmission:\n',uuid.UUID(rxtxlist[-1].senderid)," | ",str(rxtxlist[-1].msgnum)," | ",rxtxlist[-1].content,'\n')
					stream1 = p1.open(format=pyaudio.paFloat32, channels=1, rate=48000, output=True, frames_per_buffer=4096)
					stream1.write(waveform, len(waveform)//4)
					time.sleep(0.5)
					rxtxlist.pop()
					p1.terminate()				
					event_object.set()	
					event_object.clear()	
					event_object.wait()	
				p1 = pyaudio.PyAudio()				
				txmessage = messages_pb2.Message()
				txmessage.senderid = str(id)
				z = len(txmessagelist)
				txmessage.msgnum = z
				txmessage.content = str(random.random())
				txmessagelist.append(txmessage)
				waveform = ggwave.encode(txmessagelist[z].SerializeToString().decode(), protocolId = 1, volume = 25)
				print('\nTransmission:\n',uuid.UUID(txmessagelist[z].senderid)," | ",str(txmessagelist[z].msgnum)," | ",txmessagelist[z].content,'\n')
				stream1 = p1.open(format=pyaudio.paFloat32, channels=1, rate=48000, output=True, frames_per_buffer=4096)
				stream1.write(waveform, len(waveform)//4)
				time.sleep(0.5)
				p1.terminate()				
				event_object.set()	
				event_object.clear()	
				event_object.wait()	
	
	def rx(self):
		while True:
			t = time.time()	+ random.randint(15, 30)
			p2 = pyaudio.PyAudio()
			
			stream2 = p2.open(format=pyaudio.paFloat32, channels=1, rate=48000, input=True, frames_per_buffer=1024)
			
			print('\nYour ID:',id,'\n\nListening ...\n')
			instance = ggwave.init()
			
			try:
				rxmessagelist = []
				rxidlist = {}
				w = 0
				while True:
					for x in rxidlist:
						if float(rxidlist[x]) <= time.time():
							print('\nTransmitter list updated:',uuid.UUID(x),'device ID removed\n')
							rxidlist.pop(x)
							break
					data = stream2.read(1024, exception_on_overflow=False)
					res = ggwave.decode(instance, data)
					if (not res is None):
						try:
							try:
								rxmessage = messages_pb2.Message()
								rxmessage.ParseFromString(res)
								w = len(rxmessagelist)
								rxmessagelist.append(rxmessage)
								print('\nSender ID:',uuid.UUID(rxmessagelist[w].senderid),'\nMessage number:',rxmessagelist[w].msgnum,'\nReceived text:',rxmessagelist[w].content,'\n')
								if rxmessagelist[w].senderid not in rxidlist:
									rxidlist.update({rxmessagelist[w].senderid: str(time.time() + 60)})
									print('\nTransmitter list updated:',uuid.UUID(rxmessagelist[w].senderid),'device ID added\n')
									rxtxlist.append(rxmessagelist[w])
								else:
									rxidlist.update({rxmessagelist[w].senderid: str(time.time() + 60)})
									rxtxlist.append(rxmessagelist[w])
							except:
								print('\nReceived text:',res.decode("utf-8"),'\n')
						except:
							pass
					if time.time() >= t:
						stream2.stop_stream()
						stream2.close()
						event_object.set()
						event_object.clear()					
						event_object.wait()					
						t = time.time()	+ random.randint(15, 30)
						stream2 = p2.open(format=pyaudio.paFloat32, channels=1, rate=48000, input=True, frames_per_buffer=1024)
						print('\nYour ID:',id,'\n\nListening ...\n')
			except KeyboardInterrupt:
				pass
			
			ggwave.free(instance)
			
			stream2.stop_stream()
			stream2.close()
			
			p2.terminate()			
						
class_obj = rxtx()

if __name__=='__main__':
	event_object = threading.Event()

T1 = threading.Thread(target=class_obj.tx)
T2 = threading.Thread(target=class_obj.rx)

T1.start()
T2.start()
