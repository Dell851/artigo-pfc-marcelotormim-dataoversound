import ggwave
import pyaudio
import messages_pb2
import random
import time
import uuid

id = uuid.uuid4()

def tx(id, text):
	try:
		txmessagelist = []
		i = 0
		while True:
			p = pyaudio.PyAudio()
			txmessage = messages_pb2.Message()
			txmessage.senderid = str(id)
			i = len(txmessagelist)
			txmessage.msgnum = i
			txmessage.content = str(text)
			txmessagelist.append(txmessage)
			waveform = ggwave.encode(txmessagelist[i].SerializeToString().decode(), protocolId = 1, volume = 25)
			print('\nTransmission:\n',uuid.UUID(txmessagelist[i].senderid)," | ",str(txmessagelist[i].msgnum)," | ",txmessagelist[i].content,'\n')
			stream = p.open(format=pyaudio.paFloat32, channels=1, rate=48000, output=True, frames_per_buffer=4096)
			stream.write(waveform, len(waveform)//4)
			time.sleep(3)
			stream.stop_stream()
			stream.close()
	except KeyboardInterrupt:
		pass
	p.terminate()

tx(id, random.random())
