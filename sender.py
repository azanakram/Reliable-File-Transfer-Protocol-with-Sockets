#!/usr/bin/env python3

from socket import *
import pickle
import sys
import os.path
import time

# Error handling
if (len(sys.argv) != 6):
    sys.exit("Incorrect number of command line arguments")

# Invalid parameter checks   Ex: python sender.py host1 9994 9992 50 <file>
if not sys.argv[2].isdigit():
    sys.exit("Error with: " + sys.argv[2] +". Please enter a valid port number, expects integer value")

if not sys.argv[3].isdigit():
    sys.exit("Error with: " + sys.argv[3] +". Please enter a valid port number, expects integer value")

check_millisecond = sys.argv[4].split(".")
for value in check_millisecond:
    if not value.isdigit():
        sys.exit("Error with: " + sys.argv[4] +". Please enter a valid timeout interval in milliseconds")

if not os.path.isfile('./'+ sys.argv[5]):
    sys.exit("Error with: " + sys.argv[5] +". File does not exist in current directory. Please provide correct file")

# Create the Packet Class
class Packet:
    def __init__(self, type, seqnum, length, data):
        self.type = type
        self.seqnum = seqnum
        self.length = length
        self.data = data

    def __str__(self):
        return ("Packet(type= "+str(self.type)
    +", seqnum= "+str(self.seqnum)
    +", length= "+str(self.length)
    +", data= "+self.data+")")

# Declare Variables
hostname = sys.argv[1]
data_port = int(sys.argv[2])
ack_port = int(sys.argv[3])
timeout_int = float(sys.argv[4])
input_file = sys.argv[5]

with open(input_file) as file:    # Read through the file to be transferred
    data = file.read()

seqnum_log = open("seqnum.log", "w")  # Create the seqnum log file
ack_log = open("ack.log", "w")  # Create the ack log file

packet_dict = {}
seqnum = 0
data_txt = ""
counter = 0

# Split the data into packets, and store them
for i in data:
    if counter < 500: ### Max length a packet can store: 500
        data_txt += i
        counter += 1
    else:
        packet_dict[seqnum] = Packet(1, seqnum, counter, data_txt)
        seqnum += 1
        data_txt = i
        counter = 1
if counter!=0:
    packet_dict[seqnum] = Packet(1, seqnum, counter, data_txt)


# Create sockets
data_socket = socket(AF_INET, SOCK_DGRAM)   # Socket for transferring data packets
data_socket.sendto(str(ack_port).encode(), (hostname, data_port))   # Send the port number the sender will listen on for acks
ack_socket = socket(AF_INET, SOCK_DGRAM)    # Socket for transferring ACKs
ack_socket.sendto("".encode(), (hostname, ack_port))    # Send a message on ACK's socket to share address

print("Starting transfer process...")
unacked_seq = list(packet_dict.keys())
while(unacked_seq): # While we have packets that were neved ACKed, continue sending
    for packet_num in unacked_seq:
        data_packet = packet_dict[packet_num]
        packet = pickle.dumps(data_packet)  # Encode packet object with pickle
        data_socket.sendto(packet, (hostname, data_port))

        seqnum_log.write(str(packet_num)+"\n")     # Log the seqnum of the packet being sent
    
    data_socket.sendto(pickle.dumps(False), (hostname, data_port))  # Send a boolean indicator that all the unacked packets have been sent, and we await response from reciever

    resend = time.time() + (timeout_int/1000)   # We start the timer for acks to arrive

    ack_packet = pickle.loads(ack_socket.recvfrom(2048)[0])
    while(ack_packet):  # Check if we recieved an ACK packet, or a boolean value indicating no more ACKs will come
        if ack_packet.seqnum in unacked_seq:
            unacked_seq.remove(ack_packet.seqnum)

            ack_log.write(str(ack_packet.seqnum)+"\n")      # Log the seqnum of the ACK packet the Sender recieves within the timeout interval

        if (time.time() >= resend):     # We have reached the Timeout Interval. Inform client and resend all the packets that were not ACKed.
            print("Socket timed out. Resending unACKed packets...")
            break
        ack_packet = pickle.loads(ack_socket.recvfrom(2048)[0])     # Grab the boolean that indicates no more acks are enroute.

eot_packet = pickle.dumps(Packet(2, 0, 0, ""))      # Create the EOT packet
data_socket.sendto(eot_packet, (hostname, data_port))   # Send initial EOT packet

eot_confirm = pickle.loads(ack_socket.recvfrom(2048)[0])    # Get the EOT packet
if not eot_confirm:     # Check to see if it was the boolean packet that indicates the last ACK was sent.
    eot_confirm = pickle.loads(ack_socket.recvfrom(2048)[0])    # Get the EOT packet that the receiver returned
if eot_confirm.type == 2:   # Confirm it is the EOT packet
    data_socket.close()
    ack_socket.close()
    sys.exit("Transfer is complete with EOT.")      # Now that file is transferred, sender can exit.

