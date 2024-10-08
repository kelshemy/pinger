import os
import sys
import struct
import time
import select
from socket import *
import binascii

ICMP_ECHO_REQUEST = 8
rtt_min = float('+inf')
rtt_max = float('-inf')
rtt_sum = 0
rtt_cnt = 0

def checksum(string):
    csum = 0
    countTo = (len(string) / 2) * 2

    count = 0
    while count < countTo:
        thisVal = string[count + 1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(string):
        csum = csum + ord(string[len(str) - 1])
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def receiveOnePing(mySocket, ID, timeout, destAddr):
    global rtt_min, rtt_max, rtt_sum, rtt_cnt
    timeLeft = timeout
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []: # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        #Fetch the ICMP header from the IP packet
        header = recPacket[20:28]
        type, code, checksum, ID, sequence = struct.unpack("bbHHh", header)
        
        timeSent = struct.unpack("d", recPacket[28:])[0]

        if type != 8:
            rtt = (timeReceived - timeSent)  * 1000
            rtt_min = min(rtt_min, rtt)
            rtt_max = max(rtt_max, rtt)
            rtt_sum += rtt
            rtt_cnt += 1

        return (str(len(recPacket)) + " bytes from " + str(destAddr) + " ; time = " + str(rtt))

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."

def sendOnePing(mySocket, destAddr, ID):
    myChecksum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())  #8 bytes
    myChecksum = checksum(header + data)

    if sys.platform == 'darwin':
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1))

def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")
    
    mySocket = socket(AF_INET, SOCK_RAW, icmp)
    
    myID = os.getpid() & 0xFFFF 
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)

    mySocket.close()
    return delay

def ping(host, timeout=1):
    global rtt_min, rtt_max, rtt_sum, rtt_cnt
    cnt = 0
   
    dest = gethostbyname(host)
    print ("Pinging " + dest + " using Python:")
    try:
        while True:
            cnt += 1
            print (doOnePing(dest, timeout))
            time.sleep(1)
    except KeyboardInterrupt:

        rtt_avg = rtt_sum / rtt_cnt

        print("round-trip min/avg/max " + str(rtt_min) + "/" + str(rtt_avg) + "/" + str(rtt_max) + " ms")
        
if __name__ == '__main__':
    ping("127.0.0.1")

    