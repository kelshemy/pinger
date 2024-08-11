## Pinger

### Testing
Find the line that states:
 ```
 ping(“127.0.0.1”) 
 ```
 Replace the IP address within ping() with the IP of what you are testing. For example, when testing the SBU servers, I replaced ping(“127.0.0.1”) with ping(“stonybrook.edu”) and when testing a server in Copenhagen, I used ping(“185.206.224.67”). The IP address must be put within within quotation marks.

 ### Overview
 The first step that we needed to do was fetch the ICMP header from the IP packet. To do this, I used the variable, header, and set it equal to recPacket[20:28]. I only collected the 20th-28th bits of the packet since that is what holds the data we need. I then set 
 ```
 type, code, checksum, ID, and sequence = struct.unpack(“bbHHh”, header)
 ``` 
 struct.unpack will allow us to unpack from the buffer which in this case is the header and “bbHHh” represents the format string which will result in a tuple. This will mirror what we have in the sendOnePing method where 
 ```
 header = struct.pack(“bbHHh”, ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1) 
 ```
 This is because type, code, checksum, ID, sequence = struct.unpack("bbHHh", header) is in the receiveOnePing method. The next line we needed was 
 ```
 timeSent = struct.unpack(“d”, recPacket[28:])[0]
 ``` 
 This will allow us to get the time the packet was sent and we are using the data from the 28th bit onwards since that is the data that holds that information we need. We are also taking it a index 0 since without including index 0, we will be collecting the whole resultant tuple. This will mirror what was in sendOnePing, which was 
 ```
data = struct.pack("d", time.time())
 ```
Now, the next thing we needed to do was collect the round trip time information. I first created an if statement which was that if the type != 8, then we go on as type being set to 8 is for echo request. Within the if statement, I set the rtt equal to (timeReceived - timeSent) * 1000 as timeReceived - timeSent will allow us to get the round trip time currently and we times it by 1000 as that will get us the answer in ms. Now, rtt_min will be equal to min(rtt_min, rtt) as that will allow us to keep track of the minimum round trip time for each packet and rtt_max will be equal to max(rtt_max, rtt) as that will allow us to keep track of the maximum round trip time for each packet.  To find the sum of the rtt, I just add rtt to rtt_sum and to keep track of the number of rtts done, I incremented by 1 every time. To find the average of the rtts, I set rtt_avg equal to rtt_sum/rtt_cnt as to find the average, you add every rtt and divide it by the total number of rtts. 
