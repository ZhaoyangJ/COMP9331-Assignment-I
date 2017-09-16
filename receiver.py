import socket,sys
from random import randint


def makePacket(seq, ack_num, syn, ack_bit, data, fin):
	flag = 0b000
	if syn:
		flag = flag | 0b001
	if ack_bit:
		flag = flag | 0b010
	if fin:
		flag = flag | 0b100
	packet = [seq, ack_num, flag, data]
	return packet

def check_SYN(packet):
	out = packet[2] & 0b001
	return (out == 0b001)

def check_FIN(packet):
	out = packet[2] & 0b100
	return (out == 0b100)

def check_ACK(packet):
	out = packet[2] & 0b010
	return (out == 0b010)

det = 0

def OutputFile(filename, buffer):
	global byte_counter
	byte_counter += len(buffer)
	with open(filename, "a") as localfile:
		localfile.write(buffer)


def main():
	global det
	global byte_counter 

	receiver_host        = "localhost"
	#receiver_port        = int(sys.argv[1])
	#filename             = str(sys.argv[2])
	
	receiver_port     = 13000
	filename    = "test1.txt"

	receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	receiver.bind((receiver_host, receiver_port))
	
	
	ACK_received = 0
	firstAquired = False


	yseq = randint(1,9)

	sender_host = 0
	sender_port = 0
	
	destination = open(filename,'w')
	destination.close()
	
	terminate = False

	log = open('Receiver_log.txt','w')
	log.close()
	log = open('Receiver_log.txt','a')

	byte_counter = 0
	segment_counter = 0
	Num_Duplicate = 0

	In_Buffer = [] #buffer

	while True:
		if terminate:
			FINPACK = makePacket(yseq, 0,False, False, "", True)
			receiver.sendto(str(FINPACK), (sender_host, sender_port))
			terminate = False
			continue
		data, sender = receiver.recvfrom(receiver_port)
		curr_packet = eval(data)
		sender_host = sender[0]
		sender_port = sender[1]

		if (check_FIN(curr_packet)):
			if(not(int(curr_packet[1]) == int(yseq)+1 and check_ACK)):
				acktoEnd = int(curr_packet[0])+1
				terminate = True
				packet_next = makePacket(0, str(acktoEnd),False, True, "", True)
				receiver.sendto(str(packet_next), (sender_host, sender_port))
				continue
			else:
				det == 2
				log_sum(log, byte_counter, Num_Duplicate, segment_counter)
				sys.exit()
		elif (det == 0):
			byte_counter = 0
			segment_counter = 0
			Num_Duplicate = 0
			if (check_SYN(curr_packet)):
				acktoEnd = int(curr_packet[0])+1
				det = 1
				packet_next = makePacket(str(yseq), str(acktoEnd),True, True,"", False)
				receiver.sendto(str(packet_next), (sender_host, sender_port))
		elif (det == 1):
			if (not check_ACK(curr_packet)):
				segment_counter += 1
				if (int(curr_packet[0]) == 0 and not firstAquired):
					#first 
					firstAquired = True
					ACK_received = int(curr_packet[0])+int(len(curr_packet[3]))
					OutputFile(filename, str(curr_packet[3]))
				elif  (ACK_received == int(curr_packet[0]) and firstAquired):
					#new ack
					if (In_Buffer):
						Num_Duplicate+=1
						OutputFile(filename, str(curr_packet[3]))
						ACK_received =int(curr_packet[0])+int(len(curr_packet[3]))
						for i in In_Buffer:
							if (int(ACK_received) == int(i[0])):
								OutputFile(filename, str(i[3]))
								ACK_received = int(i[0])+int(len(i[3]))
						In_Buffer[:] = [value for value in In_Buffer if int(value[0])> int(ACK_received)]
					else:
						ACK_received = int(curr_packet[0])+int(len(curr_packet[3]))
						OutputFile(filename, str(curr_packet[3]))	
				else:
								#repeat ack
					In_Buffer.append(curr_packet)												
				curr_packet_ack = makePacket(0, str(ACK_received),False, True, "ack back", False)
				receiver.sendto(str(curr_packet_ack), (sender_host, sender_port))
		else:
			print "hmm.....what happen"

def log_sum(log, byte_counter, Num_Duplicate, segment_counter):
	byteNum = 'byte of data: '+str(byte_counter)+'\n'
	log.write(byteNum)
	dupNum = 'number of dup: '+str(Num_Duplicate)+'\n'
	log.write(dupNum)
	segNum = 'how many seg: '+str(segment_counter)+'\n'			
	log.write(segNum)
	log.close()

main()
