#created by sardar hassan and abdul rehman qamar aftab
from socket import *
import time
import sys
  

#set server IP, port number
serverName="127.0.0.1"
serverPort=55000
my_port=50000
file_name="to_send.mp3" #<------------------------------file to transfer
open_mode="rb" #<---------------------------------------file open mode
buffer_length=495 #set packet paylod length to 495 bytes of packet
remaining=5
sqn_num="0"
counter=0
ack_message="ACK"
nack_message="NACK"
send_again_message="Send again"
ok_message="OK"
nm_message="NM"
fin_message="FIN"
temp=0
test=False
data_buffer=[""]
sqn_num_buffer=[""]
#temp for sqn num
#temp 3 for data buffer
#temp 4 for nack sqn

clientSocket = socket(AF_INET,SOCK_DGRAM)
clientSocket.bind((serverName,my_port))

def send_data(sqn_num_buffer,data_buffer): #to send data to reciever
    temp3=len(data_buffer)
    for k in range(1,temp3):
        if sqn_num_buffer[k]!="12" and sqn_num_buffer[k]!="100":
            clientSocket.sendto(data_buffer[k] + sqn_num_buffer[k],(serverName,serverPort)) #send data one by one
            time.sleep(0.05) #wait
        #clientSocket.sendto(data_buffer[k] + sqn_num_buffer[k],(serverName,serverPort)) #send data one by one
        #time.sleep(0.05) #wait
        print "sqn num is",sqn_num_buffer[k] #print syn number

        

def check_message(sqn_num_buffer,data_buffer): #if incomming message is correct
    message,address=clientSocket.recvfrom(buffer_length)
    print "entered check message"
    while(1): #check for getting correct message
        if message[0:len(nack_message)]==nack_message: #if nack recieved
            temp3=len(data_buffer)
            print message
            while(1):
                req_sqn=message[len(nack_message):len(message)]
                for i in range(1,temp3):
                    if sqn_num_buffer[i]==req_sqn:
                        while(1):
                            clientSocket.sendto(data_buffer[i] + sqn_num_buffer[i],(serverName,serverPort))
                            time.sleep(0.05) #wait
                            message,address=clientSocket.recvfrom(buffer_length)
                            if message==ok_message:
                                break
                message,address=clientSocket.recvfrom(buffer_length)
                if message==nm_message: #if nm message recieved
                    clientSocket.sendto(ok_message,(serverName,serverPort))
                    time.sleep(0.05) #wait
                    break         
            break
        elif message==ack_message: #if ack recieved
            print message
            clientSocket.sendto(ok_message,(serverName,serverPort))
            time.sleep(0.05)
            print ok_message
            break


        
def empty_buffers(sqn_num_buffer,data_buffer):
    temp3=len(data_buffer)
    for j in range(temp3-1,0,-1): 
        data_buffer.pop(j)
        sqn_num_buffer.pop(j)
    print "remaining sqn num buffer:",sqn_num_buffer

def ask_window_size():
    #ask for window size 
    print"Asking for window size..."
    prompt="Window size?" 
    clientSocket.sendto(prompt,(serverName,serverPort))
    time.sleep(0.05)


    #get and store window size
    message,address=clientSocket.recvfrom(buffer_length)
    print "From reciever window size is",message
    return message


window_size=ask_window_size()
f = open(file_name, open_mode) #open file for reading
data=f.read(buffer_length) #get data to send
while data: #while data remaining to send



    #store data and sqn numbers in buffer
    data_buffer.append(data)
    sqn_num_buffer.append(sqn_num)
            
    if counter==int(window_size)-1:
        
        temp3=len(data_buffer)
        send_data(sqn_num_buffer,data_buffer) #send data
        check_message(sqn_num_buffer,data_buffer) #check for incominng message
        #pop sent sqn number and data

        empty_buffers(sqn_num_buffer,data_buffer) #empty the buffers
        counter=-1 #reinitialise counter
        
    temp=int(sqn_num)+1 #increment syn num
    sqn_num=str(temp)
    
    data=f.read(buffer_length) #get remaining data   
    counter += 1 

#for last few packets  
print "remaining counter is:", counter
if counter>0: #if any remaining packets
    temp3=len(data_buffer) #data buffer length
    #send data and sqn number one by one from buffer when window size reached
    send_data(sqn_num_buffer,data_buffer)
     #pop sent sqn number and data
    empty_buffers(sqn_num_buffer,data_buffer)

#send fin
clientSocket.sendto(fin_message,(serverName,serverPort))
time.sleep(0.05)

#recieve messages
check_message(sqn_num_buffer,data_buffer) #check for incominng message



clientSocket.close() #close socket
print "File closed"

