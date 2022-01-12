Programming Problem
Modelling Network Traffic (30 marks)
Your task is to develop a network traffic simulator in Python called network sim.py. This program takes as command line arguments the name of a packet trace file (located in the current working directory) and the desired number of packet arrivals in the synthetic trace that it will create. It then builds a traffic model based on the input trace and generates a synthetic trace with the desired number of arrivals following this traffic model. The synthetic trace will have the same format as the input trace (described below) and must be saved in a file called newtrace.TL in the current working directory.
Your program will be tested as follows:
Specification
Download the compressed archive BC-pAug89.TL.Z from eClass and extract it to obtain a packet trace file called BC-pAug89.TL. The trace contains information about 1,000,000 packet arrivals seen on the Ethernet at the Bellcore Morristown Research and Engineering facility in late 1989. The Ethernet carried primarily local traffic.
The input trace is in 2-column ASCII format, twenty bytes per line including the newline. The first column gives
1
the arrival time in seconds since the start of the trace . The second column is the Ethernet data length in bytes,
not including the Ethernet preamble, header, or CRC error detecting code. Note that the Ethernet protocol (IEEE 1Timestamps are floating-point numbers reported to 6 decimal places.
 $ python3 net_sim.py BC-pAug89.TL 200000 $
 2
802.3) forces all packets to have at least a frame size of 64 bytes and at most 1518 bytes (which was later expanded to 1522).
Traffic Modelling
It is up to you to decide which Markov arrival process best fits the kind of traffic you see in the input packet trace. You also have several options when it comes to modelling the packet length; recall discrete probability distributions discussed in class. The minimum requirement is that the first and second moments of the interarrival time and packet length in the synthetic trace must be very close to the respective moments in the original trace.
Many aspects are left under your control. Each one is a design decision you need to explain in a document separate from your code. For example, you should discuss: why a specific model is appropriate for packet arrivals or data lengths? how you estimated the model parameters? whether interarrival times (and packet lengths) are independent?