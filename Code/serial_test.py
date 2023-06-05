
from pylab import *
import serial, time

ion()

com = 'COM7'



class DataFrame:#With this class I decode the LiDAR info
    
    def __init__(self, verlen, speed, start_angle,points, end_angle, crc):
        self.verlen = verlen #Value set to 0x2C(1Byte) packet type (I don't use it)
        self.speed = speed #Rotation speed (2Byte)
        self.start_angle = start_angle #Start angle of the data packet (2Bytes) 0.01degree
        self.end_angle = end_angle #Angle of the end of the data packet (2Bytes) 0.01degree
        self.points = points #DATA (3Bytes) 
        self.crc = crc #crc (I don't use it)

#int.from_bytes: Create an integer from bytes

    @classmethod    
    def from_bytes(cls,buffer):#Here I create the data buffer
        verlen = buffer[0] #I don't use it
        speed = int.from_bytes(buffer[1:3], byteorder='little') #Speed ​​(2Byte 2nd and 3rd)
        start_angle = int.from_bytes(buffer[3:5], byteorder='little')*0.01 #Start angle (2Byte 3rd and 4rd)
        i = 5 #I do this to index the values ​​in the buffer skipping the previous ones
        points = [] #Here I add the distance and intensity values
        for x in range(12):
            dist = int.from_bytes(buffer[i:i+2], byteorder='little') #2 bytes of distance (5th and 6th)
            i += 2
            intensity = int.from_bytes(buffer[i:i+1], byteorder='little') #1 Byte of intensity (7th)
            i += 1
            points.append((dist,intensity)) #I add them to the 'points' list

            
        end_angle = int.from_bytes(buffer[i:i+2], byteorder='little')*0.01 #Final angle (8th)
        i += 1
        
        crc = int.from_bytes(buffer[i:i+1], byteorder='little') #I don't use it
    
        return cls(verlen, speed, start_angle, points, end_angle, crc)
        

dt = 35 # +- dt (angle)

def process_data(tt,dd): #This function restricts the range of angles

    #return array([0]),array([0]) 

    i  = logical_and(tt>(180-dt),tt<(180+dt)) #The range of angles is from 145º to 215º

    tt = tt[i] #theta
    dd = dd[i] #distance

    i = nonzero(dd) #Filter to remove errors (value 0)
    tt = tt[i] #theta
    dd = dd[i] #distance

    if tt.size<10:
        return tt,dd #Filter if I have removed most items

    i = argsort(dd) #Sort the values ​​from smallest to largest
    tt = tt[i] #theta
    dd = dd[i] #distance

    N = 6
    ttav = sum(tt[:N])/N
    ddav= sum(dd[:N])/N

    #Calculate the byte buffer of the message
    buff = int(ttav*100).to_bytes(2,"little")
    buff += int(ddav).to_bytes(2,"little")
    arduino.write(buff)
    arduino.flush()

    #print ('angle ',ttav,'distancia ', ddav)

    return tt[:N],dd[:N] 
    


#Read the serial port of the LiDAR
ser = serial.Serial(com,
                    baudrate=115200,
                    parity=serial.PARITY_NONE,
                    stopbits=1,
                    bytesize=8,
                    xonxoff=0, rtscts=0) 

#Serial port of the esp32
arduino = serial.Serial("COM6", 115200) 

time.sleep(2)





fig = figure() #Graph the position (This part is for the tests)
ax = fig.add_subplot(111)

tt = array([], dtype=float)
dd = array([], dtype=float)
xx = array([0])
yy = array([0])

line, = ax.plot(xx,yy,'k.', markersize=1)
line_data, = ax.plot(xx,yy,'r.', markersize=5)
ax.plot([-4000*cos(dt*pi/180),0,-4000*cos(-dt*pi/180)],[-4000*sin(dt*pi/180),0,-4000*sin(-dt*pi/180)])
ax.set_xlim(-4000,4000)
ax.set_ylim(-4000,4000)

while True:

    nbytes = arduino.inWaiting()#read arduino serial port
    if nbytes:#if there is something follow
        txt = arduino.read(nbytes)
        print(txt)#.decode("ascii"), end='') #Decodific ascii
    
    # wait for start of frame (x54)
    b = ser.read(1) #Read LiDAR serial port (1 byte)
    if b!= b'\x54':
        continue

    # read frame
    buffer = ser.read(46) #46 which is the length of the message

    # decode frame.
    frame = DataFrame.from_bytes(buffer) #the buffer is the 46 bytes of the message

    if frame.end_angle < frame.start_angle: #Here it corrects the error caused when a string of values ​​passes through 0º
        frame.end_angle += 360


    theta = linspace(frame.start_angle, frame.end_angle, 12)#12 points in each dataframe (creates a vector of angles)
    pts = array(frame.points, dtype=float)
    dist = pts[:,0]


    # Concatenate data making sure we don't loose the information
    # about when new scan starts. 
    if tt.size>0 and tt[-1]>theta[0]:
        theta += 360
    tt = concatenate((tt,theta))
    dd = concatenate((dd,dist))

    # check if full scan acquired.
    if tt[-1] >= 360:
        i = tt<360
        fulltt = tt[i]
        fulldd = dd[i]

        i = tt>=360
        tt = tt[i]-360
        dd = dd[i]
        
    # process tt and dd in range +-35degrees from 180
    
        ptt,pdd = process_data(fulltt,fulldd)
    
        xx = fulldd*cos(-fulltt*pi/180)
        yy = fulldd*sin(-fulltt*pi/180)
        line.set_xdata(xx)
        line.set_ydata(yy)

        xx = pdd*cos(-ptt*pi/180)
        yy = pdd*sin(-ptt*pi/180)
        line_data.set_xdata(xx)
        line_data.set_ydata(yy)

        fig.canvas.draw()
        fig.canvas.flush_events()

    
        

print(data)
