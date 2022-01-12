import pandas as pd
import sys
import numpy as np

np.set_printoptions(suppress=True, precision=7)

original_trace_file = sys.argv[1]

processor_speed = int(sys.argv[2])

# Read trace file
colnames = ['arrival_time', 'data_length']
df = pd.read_csv("./" + original_trace_file, sep='\s+', names=colnames)

# represents the number of jobs in the server
n = 0
time_elapsed = 0
arrival_number = 0
current_time = 0


# Is used to store a job's details - {arrival_time, packet_length}
class JobDetails:
    arrival_time = 0
    packet_length = 0

    def __init__(self, arrival_time, packet_length):
        self.arrival_time = arrival_time
        self.packet_length = packet_length


# A Min Heap to store jobs currently under process in the server
class ServerHeap:
    job_sizes = np.array([], dtype=float)
    job_details = []

    # returns the left child of the heap
    def leftChild(self, parent_index):
        return self.job_sizes[2 * parent_index + 1]

    # returns the right child of the heap
    def rightChild(self, parent_index):
        return self.job_sizes[2 * parent_index + 2]

    # sinks an element at position k to it's correct position among descendants
    def sink(self, k):
        n = self.job_sizes.size
        while 2 * k + 1 < n:
            leftChildIndex = 2 * k + 1
            rightChildIndex = 2 * k + 2
            if rightChildIndex < n:
                minChildIdx = rightChildIndex
                if self.job_sizes[leftChildIndex] < self.job_sizes[rightChildIndex]:
                    minChildIdx = leftChildIndex
                if self.job_sizes[minChildIdx] < self.job_sizes[k]:
                    self.exchange(minChildIdx, k)
                    k = minChildIdx
                else:
                    break
            else:
                if self.job_sizes[leftChildIndex] < self.job_sizes[k]:
                    self.exchange(leftChildIndex, k)
                    k = leftChildIndex
                else:
                    break

    # Brings up an element at position k to it's correct position among ancestors
    def swim(self, k):
        while k >= 1:
            parent_index = int((k - 1) / 2)
            if self.job_sizes[k] < self.job_sizes[parent_index]:
                self.exchange(parent_index, k)
            k = parent_index

    # insert a new element in the heap
    def insert(self, arrival_time, packet_size):
        self.job_sizes = np.append(self.job_sizes, [packet_size])
        self.job_details.append(JobDetails(arrival_time, packet_size))
        self.swim(self.job_sizes.size - 1)

    # used to swap elements of the heap
    def exchange(self, idx1, idx2):
        temp = self.job_sizes[idx1]
        self.job_sizes[idx1] = self.job_sizes[idx2]
        self.job_sizes[idx2] = temp
        self.exchangeJobDetails(idx1, idx2)

    def exchangeJobDetails(self, idx1, idx2):
        temp = self.job_details[idx1]
        self.job_details[idx1] = self.job_details[idx2]
        self.job_details[idx2] = temp

    # remove the min element of the heap
    def removeMinimum(self):
        self.exchange(0, self.job_sizes.size - 1)
        self.job_sizes = np.delete(self.job_sizes, -1)
        self.job_details.pop()
        self.sink(0)

    # get the min element of the heap
    def peekMinimum(self):
        return self.job_sizes[0]

    # get arrival time and packet length of the earliest departing job
    def getArrivalTimeAndPacketSizeOfDepartingPacket(self):
        return self.job_details[0].arrival_time, self.job_details[0].packet_length

    # given a time, calculate all remaining job sizes after that time elapses.
    # uses vectorized operations of numpy (better than O(N))
    def recomputeRemainingJobSizes(self, time_since_last_event, service_rate):
        self.job_sizes = self.job_sizes - service_rate * time_since_last_event


heap = ServerHeap()

# for calculating average response time
sum_response_time = 0
# for calculating average variance
sum_response_time_squarred = 0
# for calculating average slowdown
sum_slowdown = 0

import time

start_time = time.time()

# Loop for all arrivals
while arrival_number < df.shape[0]:
    arrival_time = df['arrival_time'][arrival_number]
    packet_length = df['data_length'][arrival_number]
    lastDepartureTime = -1
    if n > 0:
        # Next departure time is the current time + (size of the smallest remaining job) / current processor speed
        nextDepartureTime = current_time + (heap.peekMinimum() * n) / processor_speed
        while nextDepartureTime <= arrival_time:
            elapsed_time = nextDepartureTime - current_time
            # fast forwarding current time to this departure time
            current_time = nextDepartureTime
            service_rate = processor_speed / n
            # update status of all jobs to reflect their completion by this departure time
            heap.recomputeRemainingJobSizes(elapsed_time, service_rate)
            arrival_time_saved, packet_size = heap.getArrivalTimeAndPacketSizeOfDepartingPacket()
            # calculate the response time of the departing packet
            response_time = current_time - arrival_time_saved
            job_size = packet_size / processor_speed
            sum_slowdown += response_time / job_size
            sum_response_time += response_time
            sum_response_time_squarred += response_time ** 2
            # Depart the job
            heap.removeMinimum()
            lastDepartureTime = nextDepartureTime
            # reduce the number of jobs in the server by 1
            n -= 1
            if n == 0:
                break
            # check if another departure is possible before the next arrival
            nextDepartureTime = current_time + (heap.peekMinimum() * n) / processor_speed

    elapsed_time = arrival_time - current_time
    # fast-forward to the next arrival time
    current_time = arrival_time
    if n > 0 and lastDepartureTime != arrival_time:
        service_rate = processor_speed / n
        # recalculate remaining job sizes to reflect the current status of jobs in the server
        # at the time of the next arrival
        heap.recomputeRemainingJobSizes(elapsed_time, service_rate)
    n += 1
    # add the job in the server
    heap.insert(arrival_time, packet_length)
    # continue for the next arrival
    arrival_number += 1

# depart all jobs remaining in the server, after all arrivals are done
# the logic for departing jobs stay the same.
while n > 0:
    nextDepartureTime = current_time + (heap.peekMinimum() * n) / processor_speed
    elapsed_time = nextDepartureTime - current_time
    current_time = nextDepartureTime
    service_rate = processor_speed / n
    heap.recomputeRemainingJobSizes(elapsed_time, service_rate)
    arrival_time_saved, packet_size = heap.getArrivalTimeAndPacketSizeOfDepartingPacket()
    response_time = current_time - arrival_time_saved
    job_size = packet_size / processor_speed
    sum_slowdown += response_time / job_size
    sum_response_time += response_time
    sum_response_time_squarred += response_time ** 2
    heap.removeMinimum()
    n -= 1

avg_response_time = sum_response_time / df.shape[0]
avg_response_time_squarred = sum_response_time_squarred / df.shape[0]
variance = avg_response_time_squarred - (avg_response_time ** 2)
avg_slowdown = sum_slowdown / df.shape[0]

print("response time average: ", avg_response_time)
print("response time variance: ", variance)
print("slowdown average: ", avg_slowdown)
