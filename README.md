<h1>Reliable File Transfer Protocol</h1>

In this assignment we implement a reliable file transfer protocol which transfers a text file from one host to another over UDP sockets. The protocol handles network errors, and is unidirectional, that is, data flows in one direction and acknowledgements (ACKs) in the opposite direction.

Upon execution, the Sender program read through a text file, and splits the data into Packet objects (that we have created) that each store a string of up to 500 characters. We send all of our file data across our UDP data socket through these packets. Once all packets have been sent, the Sender program begins a countdown till when it will timeout (timeout is specified in execution) and stop receiving on the ACK socket, and will then retransmit all the packets who's ACK-packet from the Receiver was never read.
	
Each data packet has the chance of being dropped which is defined when the Receiving program is executed. Each data packet sent is stored and acknowledged. Once all the packets have been transferred, the Receiving program sends ACK packets indicating which packets were not dropped and have been acknowledged to the Sender. The Sender then resends all the packets that were not acknowledged, and this process repeats untill all packets have been acknowledged.
	
The Receiver program creates two log files, arrival.log which records the sequence number of each packet sent, and drop.log which records the sequence number of each data packet dropped. Similarly, the Sender program creates two log files, seqnum.log which records the sequence number of each packet sent through the socket, and ack.log which records the sequence numbers of all the ACK packets that the Sender receives during the period of transmission.
	
Once the all data packets have been sent and acknowledged, the Sender sends an EOT (End of Transmission) packet to let the Receiver know everything has been sent, upon which the Receiver then compiles all the strings in each data packet and writes it into the output textfile specified in execution. After that the Reciever sends the Sender an EOT packet as well to notify it is finished saving the new file, and Receiver exits. Sender reads the EOT packet, and notfies user transfer is complete and exits.

The Packet object had the four following fields:
- `integer** type;`		// *0: ACK, 1: Data, 2: EOT*
- `integer seqnum;`		// sequence number of the packet
- `integer length;`		// Length of the String variable 'data'
- `String data;`		// String with Max Length 500

-------------------------------------------------------
<h1>Files</h1>

We have two program files, a Sender Program (`sender.py`) and a Receiver Program (`receiver.py`).

Sender Program:
Takes in five command line inputs: `<hostname>`, `<data_port>`, `<ack_port>`, `<timeout_int>`, and `<input_file>`.

Receiver Program:
Takes in three command line inputs: `<data_port>`, `<drop_prob>`, `<output_file>`.

We also must provide *two* filenames, one for each program. The filename used in the Sender Program is the textfile whose data we are reading and transferring across. The filename used for the Receiver is the name of the file into which the received data is written. 

-------------------------------------------------------
<h1>How to run the program</h1>

We must first run the Receiver Program before we run the Sender. Navigate to the directory where receiver.py is located, and execute the following command:

	python receiver.py <data_port> <drop_prob> <output_file>

where the user specifies what port number they want to use for `<data_port>`, the drop probability `<drop_prob>`, and the filename for the `<output_file>` the program will write the received data into.

**Example:** *python receiver.py 8080 0.75 receivertest1.txt*


Now we run the Sender Program. Navigate to the directory where the Sender Program is located, and execute the following command:

	python sender.py <hostname> <data_port> <ack_port> <timeout_int> <input_file>

where the user specifies the hostname and port number they want to use for `<hostname>` and `<data_port>`, as well as what port number to use for the ACK socket `<ack_port>`, the timeout interval `<timeout_int>` in milliseconds, and the filename `<input_file>` that the program will read the data from.

**Example:** *python sender.py localhost 8080 12000 15 sendertest1.txt*

-------------------------------------------------------
