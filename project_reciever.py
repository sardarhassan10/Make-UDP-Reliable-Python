#created by sardar hassan and abdul rehman qamar aftab
from socket import *
import select
import sys
import time


window_size="10" #set window size
ip_addr="127.0.0.1" #server ip address
port_num=55000 #server port number
client_port=50000
timeout=3 #no of seconds to wait till timeout
file_to_save="from_sender.mp3" # <----------------file name where we save data 
open_mode="ab" #<----------------------------------file open mode
buffer_size=500 #set buffer length to to 500 bytes of packet
remaining=5
master_counter=0
packet_lost=False
fin_recieved=False
ack_message="ACK"
nack_message="NACK"
send_again_message="Send again"
ack_message="ACK"
nack_message="NACK"
ok_message="OK"
nm_message="NM"
fin_message="FIN"
from_us=ack_message #default from us message
sqn_num_prefix= "0" #set prefix digits of syn number
ack_num="0" #set ack number to zero
sqn_num="0"
data_buffer=[""]
sqn_num_buffer=[""]
nack_buffer=[""]
fsqn_num_buffer=[""]
temp4=[""]
temp5=[""]
counter=0
#temp 2 for storing
#temp 3 is len of data buffer
#temp 4 is for sqn num buffer, not used 
#temp 5 is for data buffer
#temp 6 for nack buffer


#bind socket
udp_sock=socket(AF_INET,SOCK_DGRAM)
udp_sock.bind((ip_addr,port_num))

#custom define bubble sort
def bubble_sort(sqn_arr,data_arr):
        temp3=len(data_arr)
        print "recieved sqn nums are:", sqn_num_buffer[1:temp3],
        index = len(sqn_arr) - 1
        while index >= 1:
                for j in range(1,index):
                        if int(sqn_arr[j]) > int(sqn_arr[j+1]):
                                sqn_arr[j], sqn_arr[j+1] = sqn_arr[j+1], sqn_arr[j]
                                data_arr[j], data_arr[j+1] = data_arr[j+1], data_arr[j]
                index -= 1
        print "reordered sqn nums are:", sqn_num_buffer[1:temp3],
        print ""
        return sqn_arr,data_arr

#storring function
def store_buffer(sqn_num_buffer,data_buffer,message,fin_recieved,sqn_num,master_counter):
        if message != fin_message: #if not FIN recieved
                temp1=len(message) #length of message
                temp2=buffer_size-len(message)
                
                if temp2==4: #for single digit sqn num
                        sqn_num=message[temp1-1]
                        print "Sqn num is",sqn_num
                        sqn_num_buffer.append(sqn_num)
                        data_buffer.append(message[0:temp1-1])
                elif temp2==3: #for double digit sqn num
                        sqn_num=message[temp1-2:temp1]
                        sqn_num_buffer.append(sqn_num)
                        print "Sqn num is",sqn_num      
                        data_buffer.append(message[0:temp1-2])
                elif temp2==2: #for three digit sqn number
                        sqn_num=message[temp1-3:temp1]
                        print "Sqn num is",sqn_num
                        sqn_num_buffer.append(sqn_num)
                        data_buffer.append(message[0:temp1-3])
                elif temp2==1: #for four digit sqn number
                        sqn_num=message[temp1-4:temp1]
                        print "Sqn num is",sqn_num
                        sqn_num_buffer.append(sqn_num)
                        data_buffer.append(message[0:temp1-3])
                elif master_counter>=10000: #for five digit sqn number
                        sqn_num=message[temp1-5:temp1]
                        print "Sqn num is",sqn_num
                        sqn_num_buffer.append(sqn_num)
                        data_buffer.append(message[0:temp1-3])
                else: #for file data less than buffer_size - remaining
                        if master_counter<10: #for single digit sqn num
                                sqn_num=message[temp1-1]
                                print "Sqn num is",sqn_num
                                sqn_num_buffer.append(sqn_num)
                                data_buffer.append(message[0:temp1-1])
                        elif master_counter<100: #for double digit sqn num 
                                sqn_num=message[temp1-2:temp1]
                                print "Sqn num is",sqn_num
                                sqn_num_buffer.append(sqn_num)
                                data_buffer.append(message[0:temp1-2])
                        elif master_counter<1000: #for triple digit sqn num
                                sqn_num=message[temp1-3:temp1]
                                print "Sqn num is",sqn_num
                                sqn_num_buffer.append(sqn_num)
                                data_buffer.append(message[0:temp1-3])
                        elif master_counter<10000: #for four digit sqn num
                                sqn_num=message[temp1-4:temp1]
                                print "Sqn num is",sqn_num
                                sqn_num_buffer.append(sqn_num)
                                data_buffer.append(message[0:temp1-4])
                        elif master_counter<100000: #for five digit sqn num
                                sqn_num=message[temp1-5:temp1]
                                print "Sqn num is",sqn_num
                                sqn_num_buffer.append(sqn_num)
                                data_buffer.append(message[0:temp1-5])
                        
        else:
                fin_recieved=True
        return sqn_num,sqn_num_buffer,data_buffer,fin_recieved
        
def send_ack(): #send ack
        udp_sock.sendto(ack_message,(ip_addr,client_port)) #send ack
        time.sleep(0.05)
        print ack_message

def empty_buffers(data_buffer,sqn_num_buffer,nack_buffer): #empty buffers
        temp3=len(data_buffer)
        for k in range(temp3-1,0,-1):
                data_buffer.pop(k)
                sqn_num_buffer.pop(k)
        #empty nack buffer
        if len(nack_buffer)>1:
                temp6=len(nack_buffer)
                for k in range(temp6-1,0,-1):
                        nack_buffer.pop(k)
        return data_buffer,sqn_num_buffer,nack_buffer                      

        
def send_correct_message(from_us):
        while(1): #check for getting correct message
                message, address = udp_sock.recvfrom(buffer_size) #get message
                print message
                if message==send_again_message: #if asked to send again
                        udp_sock.sendto(ack_message,(ip_addr,client_port)) #send message
                        time.sleep(0.05)
                elif message==ok_message:
                        break

def give_window_size(message,counter,master_counter):
        if message=="Window size?": #if window size asked 
                print "Sender:",address[0],", message:",message #print the in comming message
                udp_sock.sendto(window_size,(ip_addr,client_port)) #send the window size
                time.sleep(0.05)
                counter=-1 #reinitialise counter
                master_counter=-1
        else:
                for i in range(buffer_size-3):
                        f1.writelines(message[i]) #write incomming data
                print "Data coming from ip address:",address[0]
                sqn_num=message[buffer_size-3:len(message)]
                print "sqn num is ", sqn_num #print single digit sqn number to shell
                counter=counter+1
                master_counter=master_counter+1
                

        return master_counter,counter

def check_missing(master_counter,counter,sqn_num_buffer,data_buffer,packet_lost,from_us,fin_recieved):
        temp3=len(data_buffer)
        t=master_counter-counter
        i=1
        while i<temp3:
                if sqn_num_buffer[i]!=str(t+i-1): #if sqn num missing
                        packet_lost=True
                        #ask for missing packet
                        while(1):
                                udp_sock.sendto(nack_message+str(t+i-1),(ip_addr,client_port)) #send nack
                                time.sleep(0.05)
                                message, address = udp_sock.recvfrom(buffer_size) #get packet
                                master_counter +=1 #increment master counter
                                counter += 1 #increment counter

                                sqn_num,sqn_num_buffer,data_buffer,fin_recieved= store_buffer(sqn_num_buffer,data_buffer,message,fin_recieved,sqn_num_buffer[i],master_counter)
                                sqn_num_buffer,data_buffer=bubble_sort(sqn_num_buffer,data_buffer)
                                
                                if sqn_num_buffer[i]==str(t+i-1): #if correct recieved
                                        #send ok
                                        udp_sock.sendto(ok_message,(ip_addr,client_port))
                                        print ok_message
                                        if temp3 <= int(window_size)+1: #while temp3 is in range
                                                temp3 +=1 #increment temp3
                                        break
                i+=1 #increment i

                
        if len(data_buffer) != int(window_size)+1: #buffer not full
                if fin_recieved==False:
                        while(len(data_buffer) != int(window_size)+1) and fin_recieved==False:
                                
                                #send nack
                                udp_sock.sendto(nack_message+str(t+i-1),(ip_addr,client_port)) #send nack
                                print str(t+i-1)
                                time.sleep(0.05)
                                
                                message, address = udp_sock.recvfrom(buffer_size) #get packet
                                packet_lost=True
                                master_counter +=1 #increment master counter
                                counter += 1 #increment counter

                                sqn_num,sqn_num_buffer,data_buffer,fin_recieved= store_buffer(sqn_num_buffer,data_buffer,message,fin_recieved,sqn_num_buffer[i-1],master_counter)
                                sqn_num_buffer,data_buffer=bubble_sort(sqn_num_buffer,data_buffer)

                                if sqn_num_buffer[i]==str(t+i-1): #if correct recieved
                                        #send ok
                                        udp_sock.sendto(ok_message,(ip_addr,client_port))
                                        print ok_message
                                        if temp3 <= int(window_size)+1: #while temp3 is in range
                                                temp3 +=1 #increment temp3
                                i +=1


                        
        if packet_lost==False:
                #print ack
                send_ack()
                from_us=ack_message
                
        #send No more messgae
        if packet_lost==True:
                udp_sock.sendto(nm_message,(ip_addr,client_port))
                print nm_message
        return sqn_num_buffer,data_buffer,from_us,packet_lost,master_counter,counter,fin_recieved

                
print "ready to serve"

#main while loop
while True:
        f1=open(file_to_save,open_mode) #open file for appending
        message, address = udp_sock.recvfrom(buffer_size) #recieve message
        if message: #if message recieved
                master_counter,counter=give_window_size(message,counter,master_counter)
                while True:  #secondary loop
                        temp=select.select([udp_sock],[],[],timeout) 
                        if temp[0]: #if messages still coming
                                packet_lost=False
                                master_counter += 1
                                counter += 1
                                message, address = udp_sock.recvfrom(buffer_size)
                                
                                #storring function
                                sqn_num,sqn_num_buffer,data_buffer,fin_recieved=store_buffer(sqn_num_buffer,data_buffer,message,fin_recieved,sqn_num,master_counter)
                                                                        

                                #print "time difference=",time_difference
                                if (counter==int(window_size)-1 ): #if window size reached
                                        
                                        temp3=len(data_buffer) #length of data buffer
                                        #reordering of packets
                                        sqn_num_buffer,data_buffer=bubble_sort(sqn_num_buffer,data_buffer)

                                        #check for missed packets
                                        sqn_num_buffer,data_buffer,from_us,packet_lost,master_counter,counter,fin_recieved= check_missing(master_counter,counter,sqn_num_buffer,data_buffer,packet_lost,from_us,fin_recieved)
                                        send_correct_message(from_us)

                                        packet_lost=False
                                        f1.writelines(data_buffer[1:temp3])

                                        #empty buffers
                                        data_buffer,sqn_num_buffer,nack_buffer=empty_buffers(data_buffer,sqn_num_buffer,nack_buffer)
                                        counter=-1 #reinitiase counter
                                                   
                        elif not temp[0]: #no incoming data
                                #check for packet loss
                                sqn_num_buffer,data_buffer,from_us,packet_lost,master_counter,counter,fin_recieved= check_missing(master_counter,counter,sqn_num_buffer,data_buffer,packet_lost,from_us,fin_recieved)
                                #to see if correct message sent
                                if fin_recieved==False or (master_counter+1)%int(window_size)!=0: #if not end of transfer
                                        send_correct_message(from_us)

                                if packet_lost==False:
                                        #reordering of packets
                                        sqn_num_buffer,data_buffer=bubble_sort(sqn_num_buffer,data_buffer)
                                        
                                temp3=len(data_buffer) #length of data buffer
                                print "remaining buffer size is",temp3

                                
                                #write data in to file
                                if counter >=0:
                                        f1.writelines(data_buffer[1:temp3])
                                        #clean up buffers
                                        data_buffer,sqn_num_buffer,nack_buffer=empty_buffers(data_buffer,sqn_num_buffer,nack_buffer)
                                        counter=-1 #reinitialise counter

                                #close file
                                if packet_lost==False or fin_recieved==True:
                                        f1.close()
                                        print "file closed"
                                        if fin_recieved==True:
                                                print fin_message
                                                fin_recieved==False #reset fin recieved
                                        break #break secondary loop
                        
udp_sock.close() #close socket

