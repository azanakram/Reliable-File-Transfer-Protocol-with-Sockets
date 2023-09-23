#!/usr/bin/env python3

from socket import *
import sys
import os.path
import random
import pickle

# Error handling
if (len(sys.argv) != 4):
    sys.exit("Incorrect number of command line arguments")

# Invalid parameter checks   Ex: python receiver.py 9994 0.5 <file>
if not sys.argv[1].isdigit():
    sys.exit("Error with: " + sys.argv[1] +". Please enter a valid port number, expects integer value")

try:
    float(sys.argv[2])
except ValueError:
    sys.exit("Error with: " + sys.argv[2] +". Please enter a valid drop probability, expects decimal between 0 and 1")

if (float(sys.argv[2])<0) or (float(sys.argv[2])>1):
    sys.exit("Error with: " + sys.argv[2] +". Please enter a valid drop probability, expects integer value")

if not os.path.isfile('./'+ sys.argv[3]):
    sys.exit("Error with: " + sys.argv[3] +". File does not exist in current directory. Please provide correct file")

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
data_port = int(sys.argv[1])
drop_prob = float(sys.argv[2])
output_file = sys.argv[3]

# Create sockets
data_socket = socket(AF_INET, SOCK_DGRAM)   # Create socket where data will be transferred
data_socket.bind(('', data_port))   # Bind the socket to the port number
ack_port = data_socket.recvfrom(2048)[0]  # Get the port number for the ACK socket

ack_port = int(ack_port.decode())
ack_socket = socket(AF_INET, SOCK_DGRAM)    # Create the ACK socket
ack_socket.bind(('', ack_port))     # Bind the ACK socket to the ACK port
temp, ack_address = ack_socket.recvfrom(2048)   # Get the address for the ACK socket

packet_dict = {}

arrival_log = open("arrival.log", "w")  # Create the arrival log file
drop_log = open("drop.log", "w")    # Create the drop log file

eot_recieved = False    # Flag false that EOT packet has not been received
acks = []   # List to track what data packets where ACKed in each instance of transfer
while True:
    while True:
        packet = pickle.loads(data_socket.recvfrom(2048)[0])    # Receive data packets
        if packet:
            if packet.type == 2: # If it is an EOT packet, change flag to true and break out of the loop
                print("All packets have been transferred and acked")
                eot_recieved = True
                break
            
            not_dropped = random.random()   # Get a random value between 0 and 1, to see if we drop it or not
            
            if not_dropped >= drop_prob: # Data packet that is NOT dropped
                arrival_log.write(str(packet.seqnum)+"\n")      # write in the arrival.log file the seqnum of the packets recieved
                
                if packet.seqnum not in packet_dict:    # if packet is not a duplicate, store it and ACK it
                    packet_dict[packet.seqnum] = packet
                    acks.append(packet.seqnum)
            
            else:   # Packets that are dropped
                drop_log.write(str(packet.seqnum)+"\n")     # write in the drop.log file the seqnum of the packets dropped
                
        else:   # All data packets have been sent. Now we must returned what we have ACKed
            if not acks:
                ack_socket.sendto(pickle.dumps(False), ack_address)     # If nothing left to ACK, send a prompt to sender to send the EOT file
                break
            for ack_num in acks:
                ack_packet = pickle.dumps(Packet(0, ack_num, 0, ""))    # Create the ACK packet and encode it with pickle
                ack_socket.sendto(ack_packet, ack_address)      # Send the ACK packet to the sender
            ack_socket.sendto(pickle.dumps(False), ack_address)     # Send boolean packet to indicate all ACKs have been sent
            acks = []   # Clear ACK list to start process again
    
    if eot_recieved:    # If EOT packet has been recieved, stop waiting for packets as all the data is transferred
        print("EOT file has been received.")
        break

sorted_packets = sorted(packet_dict.keys())
compiled_data = ""

for seqnum in sorted_packets:      # Compile the information in each data packet in order
    compiled_data += packet_dict[seqnum].data

arrival_log.close()     # Close arrival log file
drop_log.close()    # Close drop log file

with open(output_file, "w") as file:       # Write into the provided output file the contents of what was transferred.
    file.write(compiled_data)

eot_packet = pickle.dumps(Packet(2, 0, 0, ""))      # Create EOT packet to send back to sender
ack_socket.sendto(eot_packet, ack_address)

sys.exit("Transfer is complete.")   # Now that everything is done, the reciever can Exit.