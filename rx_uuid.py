import ggwave
import pyaudio
import messages_pb2
import random
import time
import uuid

id = uuid.uuid4()

def receptor(id):
	p = pyaudio.PyAudio()
	stream = p.open(format=pyaudio.paFloat32, channels=1, rate=48000, input=True, frames_per_buffer=1024)
	print('\nYour ID:',id,'\n\nListening ...\n')
	instance = ggwave.init()
	try:
		rxmessagelist = []
		rxidlist = {}
		i = 0
		while True:
			for x in rxidlist:
				if float(rxidlist[x]) <= time.time():
					print('\nTransmitter list updated:',uuid.UUID(x),'device ID removed\n')
					rxidlist.pop(x)
					break
			data = stream.read(1024, exception_on_overflow=False)
			res = ggwave.decode(instance, data)
			if (not res is None):
				try:
					rxmessage = messages_pb2.Message()
					rxmessage.ParseFromString(res)
#					print(rxmessage)
					i = len(rxmessagelist)
					rxmessagelist.append(rxmessage)
					print('\nSender ID:',uuid.UUID(rxmessagelist[i].senderid),'\nMessage number:',rxmessagelist[i].msgnum,'\nReceived text:',rxmessagelist[i].content,'\n')
					if rxmessagelist[i].senderid not in rxidlist:
						rxidlist.update({rxmessagelist[i].senderid: str(time.time() + 20)})
						print('\nTransmitter list updated:',uuid.UUID(rxmessagelist[i].senderid),'device ID added\n')
					else:
						rxidlist.update({rxmessagelist[i].senderid: str(time.time() + 20)})
				except:
					pass
	except KeyboardInterrupt:
		pass
	ggwave.free(instance)
	stream.stop_stream()
	stream.close()
	p.terminate()

receptor(id)
