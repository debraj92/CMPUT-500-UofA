import pandas as pd
import sys

original_trace_file = sys.argv[1]
k = int(sys.argv[2])
if k == 0:
    print("There must be space for at least one packet in the gateway")
    sys.exit()

gateway_l = int(sys.argv[3])
simulation_time = int(sys.argv[4])

colnames = ['arrival_time', 'data_length']
df = pd.read_csv("./" + original_trace_file, sep='\s+', names=colnames)

# Queue of capacity k+1 (including packet in server)
# Each element of the queue would contain the departure time of that packet.

q = []
idle_time = 0
# To find E[N]
total_packets_in_system = 0
total_arrivals = 0

time_elapsed = 0
lastDepartureTime = 0
arrival_number = 0
total_packets_dropped = 0
total_packets_departed = 0


def getPacketProcessingTime(packet_length):
    global gateway_l
    return packet_length / gateway_l


def isQueueFull(q):
    global k
    return len(q) == k + 1


while time_elapsed < simulation_time and arrival_number < df.shape[0]:
    arrival_time = df['arrival_time'][arrival_number]
    packet_length = df['data_length'][arrival_number]
    total_arrivals += 1

    if not q:
        # if Q is empty.
        # Next event is : Arrival
        # Until next event, server is idle
        time_elapsed = arrival_time
        idle_time += arrival_time - lastDepartureTime
        q.append(arrival_time + getPacketProcessingTime(packet_length))
    else:
        # Q has packets
        # First we dequeue packets whose departure time is before the
        # arrival time of the current packet.
        while q and q[0] < arrival_time:
            time_elapsed = q.pop(0)
            total_packets_departed += 1
            lastDepartureTime = time_elapsed

        # next event is arrival
        time_elapsed = arrival_time

        # if all packets are dequeued server is idle until next arrival
        if not q:
            idle_time += arrival_time - lastDepartureTime
            q.append(arrival_time + getPacketProcessingTime(packet_length))
        else:
            if isQueueFull(q):
                # if queue is full, packet would be dropped
                total_packets_dropped += 1
                total_packets_in_system += len(q)
            else:
                # departure time of this packet = departure time of previous packet + this packet's
                # processing time
                total_packets_in_system += len(q)
                q.append(q[-1] + getPacketProcessingTime(packet_length))

    arrival_number += 1

# if all arrivals are processed but simulation has not ended. We need to pop remaining 
# packets from the queue.
while q and time_elapsed < simulation_time:
    time_elapsed = q.pop(0)
    total_packets_departed += 1


avg_packets_in_system = total_packets_in_system / total_arrivals

print("no. packets sent out:", total_packets_departed)
print("no. blocked arrivals:", total_packets_dropped)
print("idle time of the server:", idle_time)
print("average number of packets seen in the gateway:", avg_packets_in_system)


