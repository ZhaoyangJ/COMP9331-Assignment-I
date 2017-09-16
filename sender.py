import socket
import sys
import time
import random
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

segment_count = 0
byte_counter = 0
droppedCount = 0
Num_retransmitted = 0
Num_duplicate = 0

def main():

	#receiver_host = str(sys.argv[1])
	#receiver_port = int(sys.argv[2])
	#file_to_read = str(sys.argv[3])
	#mws = int(sys.argv[4])  #max window size
	#mss = int(sys.argv[5])  #max segmanet size
	#timeout_in = float(sys.argv[6])
	#pdrop = float(sys.argv[7]) #packetdrop probability
	#seed = int(sys.argv[8])
	#receiver_address = (receiver_host, receiver_port)

	receiver_host      = "localhost"
	receiver_port      = 13000
	receiver_address   = (receiver_host, receiver_port)
	file_to_read   	   = "test2.txt"
	mws          	   = 500
	mss                = 50
	timeout_in         = 2.5
	seed               = 300

	pdrop     		   = 0.3
	
	global byte_counter
	global segment_count  
	global droppedCount  
	global Num_retransmitted  
	global Num_duplicate  

	timeout = timeout_in
	time_stamp = time.time()*1000
	sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sender.settimeout(1)
	log = open('Sender_log.txt','w')
	log.close()
	log = open('Sender_log.txt','a')
	
	handshake(log, time_stamp, sender, receiver_address)
	
	#source_Data = read_From_file(file_to_read)

	send_Packet(log, time_stamp,sender, receiver_address, file_to_read, mws, mss, pdrop, seed, timeout)

	ConnShutDown(log, time_stamp, sender, receiver_address)

def read_From_file(file_to_read):
	try:
		content = open(file_to_read, "r")
		file = content.read()
		content.close()
		return file
	except IOError:
		sys.exit("FNF")



def log_SYN(log, elapsed, initial_seq, SYN_packet):
	transmission_info = 'snd\t'+str(elapsed)+'\tS\t'+str(initial_seq)+'\t'+str(len(SYN_packet[3]))+'\t'+str(SYN_packet[1])+'\n'
	log.write(transmission_info)

def log_SA(log, elapsed, SYNACK_packet):
	transmission_info = 'rcv\t'+str(elapsed)+'\tSA\t'+str(SYNACK_packet[0])+'\t'+str(len(SYNACK_packet[3]))+'\t'+str(SYNACK_packet[1])+'\n'
	log.write(transmission_info)

def log_A_HS(log, elapsed, ACK_packet_HS):
	transmission_info = 'snd\t'+str(elapsed) + '\tA\t' + str(ACK_packet_HS[0])+'\t'+ '0\t' +str(ACK_packet_HS[1])+'\n'
	log.write(transmission_info)

def handshake(log,time_stamp,sender, receiver_address):
		# generate a random seq for starter
	initial_seq = randint(0,255)
							#seq, ack_num, syn, ack_bit, fin, data
	SYN_packet = makePacket(str(initial_seq), 0, True, False, "", False)

	sender.sendto(str(SYN_packet), receiver_address)
	elapsed = time.time()*1000-time_stamp
	log_SYN(log, elapsed, initial_seq, SYN_packet)
	
	try:
		feedback, receiver_address = sender.recvfrom(1024)
		SYNACK_packet = eval(feedback)
		if (check_SYN(SYNACK_packet) and check_ACK(SYNACK_packet) and (int(SYNACK_packet[1]) == (initial_seq+1))):					
			elapsed = time.time()*1000-time_stamp
			log_SA(log, elapsed, SYNACK_packet)

			ACK_packet_HS = makePacket(0, str(int(SYNACK_packet[0])+1), False, True, "" ,False)
			sender.sendto(str(ACK_packet_HS), receiver_address)
			elapsed = time.time()*1000-time_stamp
			log_A_HS(log, elapsed, ACK_packet_HS)
			return
		else :
			print "impossible"

	except socket.timeout:
		sys.exit()

def log_first_FIN(log, elapsed, initial_seq, First_FIN):
	transmission_info = 'snd\t'+str(elapsed)+'\tF\t'+str(initial_seq)+'\t'+str(len(First_FIN[3]))+'\t'+str(First_FIN[1])+'\n'
	log.write(transmission_info)

def log_lastPacket(log, elapsed, lastPacket):
	transmission_info = 'snd\t'+str(elapsed)+'\tA\t'+str(lastPacket[0])+'\t'+str(len(lastPacket[3]))+'\t'+str(lastPacket[1])+'\n'
	log.write(transmission_info)

def log_sum(log, byte_counter, segment_count, droppedCount, Num_retransmitted, Num_duplicate):
	byteNum = 'bytes: '+str(byte_counter)+'\n'
	log.write(byteNum)
	segNum = 'data seg: '+str(segment_count)+'\n'
	log.write(segNum)
	dropNum = 'dropped: '+str(droppedCount)+'\n'
	log.write(dropNum)
	retransNum = 'retransmitted: '+str(Num_retransmitted)+'\n'
	log.write(retransNum)
	dupNum = 'how many dup: '+str(Num_duplicate)+'\n'
	log.write(dupNum)
	log.close()

def ConnShutDown(log, time_stamp, sender, receiver_address):

	global byte_counter  
	global segment_count  
	global droppedCount  
	global Num_retransmitted  
	global Num_duplicate  
	initial_seq = randint(0,255)
					#seq, ack_num, syn, ack_bit, fin, data
	First_FIN = makePacket(str(initial_seq), 0, False, False, "", True)
	sender.sendto(str(First_FIN), receiver_address)
	elapsed = time.time()*1000-time_stamp
	log_first_FIN(log, elapsed, initial_seq, First_FIN)
	
	while True:
		try:
			feedback, receiver_address = sender.recvfrom(1024)
			FINACK = eval(feedback)

			if (check_FIN(FINACK) and not check_ACK(FINACK)):
				
				lastPacket = makePacket( 0, str(int(FINACK[0])+1), False, True, "", True)	
				sender.sendto(str(lastPacket), receiver_address)
				elapsed = time.time()*1000-time_stamp
				log_lastPacket(log, elapsed, lastPacket)
			
				log_sum(log, byte_counter, segment_count, droppedCount, Num_retransmitted, Num_duplicate)
				
				sys.exit()
			else :
				#time.time()*1000-time_stamp = time.time()*1000-time_stamp
				transmission_info = 'rcv\t'+str(time.time()*1000-time_stamp)+'\tFA\t'+str(FINACK[0])+'\t'+str(len(FINACK[3]))+'\t'+str(FINACK[1])+'\n'
				log.write(transmission_info)
		except socket.timeout:
			print ("timed out in terminate")
			sys.exit()


def send_Packet(log, time_stamp,sender, receiver_address, file_to_read, mws, mss, pdrop, seed,timeout):
	
	global segment_count  
	global droppedCount  
	global Num_retransmitted  
	global Num_duplicate

	reference = time.time()*1000
	send_Base = -1 
	seq = 0; 		
	window = []
	count = 0
	initial_ack = -1
	window_size = mws/mss
	random.seed(seed)
	source_Data = read_From_file(file_to_read)
	while (True):
		
		while (not window or len(window) < window_size and seq <= len(source_Data)):
			if(len(window)>0 and (time.time()*1000-reference >=  timeout) and int(send_Base) == int(window[0][0])):
				#timeout event
				reference = time.time()*1000
				Num_retransmitted+=1
				if ((int(window[0][0]) + mss) >= len(source_Data)):
					DSegment = source_Data[int(window[0][0]):]
				else:				
					DSegment = source_Data[int(window[0][0]):int(window[0][0])+mss]
				newPacket = makePacket(int(window[0][0]), 0, False, False, DSegment, False)
				PLD(log,time_stamp,sender, newPacket, receiver_address,pdrop)

			if ((seq + mss) >= len(source_Data)):
				DSegment = source_Data[seq:]
			else:
				DSegment = source_Data[seq:seq+mss]
			newPacket = makePacket(seq, 0, False, False, DSegment, False)
			window.append(newPacket)
			send_Base = int(window[0][0])

			seq = seq + mss
			PLD(log,time_stamp,sender, newPacket, receiver_address,pdrop)

		try:
			feedback, receiver_address = sender.recvfrom(1024) # listen to ack for data packets
			received_packet = eval(feedback)
			#time.time()*1000-time_stamp = time.time()*1000-time_stamp
			transmission_info = 'rcv\t'+str(time.time()*1000-time_stamp)+'\tA\t'+str(received_packet[0])+'\t'+str(len(received_packet[3]))+'\t'+str(received_packet[1])+'\n'
			log.write(transmission_info)
			#del the success ack
			if check_ACK(received_packet):
				max_ack = window[len(window)-1][0]
				if(int(received_packet[1]) >= len(source_Data)):
					# reach to a stage where it's ok to terminate the whole thing
					break
				if(initial_ack == int(received_packet[1])):
					count += 1
					Num_duplicate += 1
				if (count >= 2):
					retransmition(log,time_stamp,sender, receiver_address,pdrop,received_packet[1],window,mss,source_Data)
					count = 0

				initial_ack = int(received_packet[1])
				for tracks in window:
					if int(int(tracks[0])+int(len(tracks[3])))> int(received_packet[1]):
						reference = time.time()*1000
				window[:] = [tracks for tracks in window if int(int(tracks[0])+int(len(tracks[3])))> int(received_packet[1])]

			 
		except socket.timeout:
			if ((int(window[0][0]) + mss) < len(source_Data)):
				DSegment = source_Data[int(window[0][0]):int(window[0][0])+mss]
			else:
				DSegment = source_Data[int(window[0][0]):]
			newPacket = makePacket(int(window[0][0]), 0, False, False, DSegment, False)
			PLD(log,time_stamp,sender, newPacket, receiver_address,pdrop)

def retransmition(log, time_stamp, sender, receiver_address, pdrop, seq, window, mss, source_Data):
	
	global droppedCount  
	#global Num_duplicate
	#global segment_count
	global Num_retransmitted   
	if ((int(seq) + mss) >= len(source_Data)):
		DSegment = source_Data[int(seq):]
	else:
		DSegment = source_Data[int(seq):int(seq)+mss]
	newPacket = makePacket(int(seq), 0, False, False, DSegment, False)
	Num_retransmitted+=1
	PLD(log,time_stamp,sender, newPacket, receiver_address, pdrop)
	
def log_newPacket_drop(log, elapsed, newPacket):
	transmission_info = 'drop\t'+str(elapsed)+'\tD\t'+str(newPacket[0])+'\t'+str(len(newPacket[3]))+'\t'+str(newPacket[1])+'\n'
	log.write(transmission_info)

def log_newPacket_snt(log, elapsed, newPacket):
	transmission_info = 'snd\t'+str(elapsed)+'\tD\t'+str(newPacket[0])+'\t'+str(len(newPacket[3]))+'\t'+str(newPacket[1])+'\n'
	log.write(transmission_info)

def PLD(log,time_stamp,sender, newPacket, receiver_address, pdrop):

	global byte_counter  
	global droppedCount 
	global segment_count  
	
	rand = random.random()
	segment_count +=1
	if (rand <= pdrop):
		droppedCount += 1
		elapsed = time.time()*1000-time_stamp
		log_newPacket_drop(log, elapsed, newPacket)
	else:
		sender.sendto(str(newPacket), receiver_address)
		byte_counter += len(newPacket[3])
		elapsed= time.time()*1000-time_stamp
		log_newPacket_snt(log, elapsed, newPacket)

main()

