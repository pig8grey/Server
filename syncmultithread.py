# -*- coding: utf-8 -*-
#Version 1.0.0

from obspy import Stream
import sys
import functools  
if sys.version_info[0]>=3:
    from tkinter import *   # python3
    from tkinter.filedialog import *
    from tkinter.messagebox import *
    from tkinter.ttk import Treeview, Style

else: 
    from Tkinter import * 
    from tkFileDialog import *
    from tkMessageBox import *
    from ttk import Treeview, Style


from threading import Thread
from time import sleep,time
import socket
import os
import struct
import numpy as np
from datetime import datetime
from seedwrite import writeseed
from seedwrite import trace_gen,writestream




##TODO:Correct the fact that we are closing the whole socket when something happened within one connection


        
def gettime():
    t=datetime.utcnow().isoformat()
    t=t+'  --->  '
    return t

def unpack(data):
    
    critnumber='<'+str(int(len(data)/4))+'f'
#    critnumber='>'+str(int(len(data)/4))+'f'
    results=struct.unpack(critnumber,data)  
    return results

##for closing server only##


    
class Gui(Frame):
    __slots__ = ('selectedbox','desiredbox','logger','clidisp','ls','tgtbox',\
                 'thread','dir','running','startb','cliententry','commandlist','clientnum',
                 'scale'\
                     )
    def __init__(self,master):
        Frame.__init__(self, master)
        xpos=0.05
        self.running = 0    #not listening

        self.debug=BooleanVar()
        self.debug.set(False)
        
        
        self.frame = Frame(colormap='new')
        self.frame.place(relx=xpos ,rely=0.67)
        self.startb = Button(self.frame, text = "Start Server", command = self.startc,height=2, width=20,\
                             bg='#90ee90')
        self.startb.pack(side = LEFT, anchor = S)

        self.connectionl = Label(self.frame, text = "OFF.",height=2,bg='#ff5f5f')
        
        self.connectionl.pack(side = LEFT, anchor = E,expand=YES)
        self.expertmode=BooleanVar()
        self.expertmode.set(False)
        self.showexpert = Checkbutton( text='Expert Mode',variable=self.expertmode, command=self.placeframe)
        self.showexpert.place(relx=xpos,rely=0.74)
        
        self.framecommand=Frame()

        self.commandlabel=Label(self.framecommand,text='Command to Client: ')
        self.commandtext=Entry(self.framecommand, width=15)
        self.cliententry=Entry(self.framecommand, width=10)
        self.addrlabel=Label(self.framecommand,text='Client Box ID: ')
        self.sendbutton=Button(self.framecommand,text='Send Command\nto Client', width=12,height=4\
                               ,command=self.send_command)

        self.tgtbox=None
        
        
        self.logoframe=Frame()
        self.logoframe.place(relx=xpos,rely=0.04)
        self.logo=PhotoImage(file=os.path.join('images','logo2.png'))
        self.logolabel=Label(self.logoframe,image=self.logo)
        self.logolabel.pack ()
   
        
        self.cliframe=Frame(colormap='new')
        self.cliframe.place(relx=0.4,rely=0.1)

#        self.condisp=Listbox (self.cliframe,width=80,height=12)
        self.scrollbartop=Scrollbar(self.cliframe)
        self.clidisp=Treeview(self.cliframe,height=12)
        self.clidisp['show'] = 'headings'
        self.clidisp['columns'] = ('boxid', 'ip')
        self.clidisp.heading('ip', text='IP')
        self.clidisp.heading('boxid', text='Box ID')
        self.clidisp.column('boxid', width=152)
        self.clidisp.column('ip', width=490)
        self.clidisp.pack(side=LEFT,fill=Y)

#        self.condisp.pack(side=LEFT,fill=Y)
        self.scrollbartop.pack(side=RIGHT,fill=Y)
        self.scrollbartop.config(command=self.clidisp.yview)
        self.clidisp.config(yscrollcommand=self.scrollbartop.set)

        self.conntitle=Label(text='Connected Clients↓ ')
        self.conntitle.place(relx=0.4, rely=0.05)
        self.cdframe=Frame(colormap='new')
        self.cdframe.place(relx=0.7,rely=0.05)
        self.numtitle=Label(self.cdframe,text='Total Connected Clients: ',\
                            bg='#ff5f5f')

        
        self.clientnum=Label(self.cdframe,text=str(len(self.clidisp.get_children())),\
                             bg='#ff5f5f',font=("", 16))   
        
        self.numtitle.pack(side=LEFT)
        self.clientnum.pack(side=LEFT)        
        
        self.checkdebug = Checkbutton( text='Debug Mode',variable=self.debug)
        self.checkdebug.place(relx=0.6,rely=0.5)
        self.logtitile=Label(text='Logs↓ ')
        self.logtitile.place(relx=0.4,rely=0.5)
        self.scrolltext=Frame(colormap='new')
        self.scrolltext.place(relx=0.4,rely=0.55)
        
        if sys.platform.startswith('win'):
            self.logger=Text (self.scrolltext,state=DISABLED,height=16,width=71)
        else:
            self.logger=Text (self.scrolltext,state=DISABLED,height=15,width=64)
        
        self.scrollbar=Scrollbar(self.scrolltext)
        self.logger.pack(side=LEFT,fill=Y)
        self.scrollbar.pack(fill=BOTH,expand=True)
        self.scrollbar.config(command=self.logger.yview)
        self.logger.config(yscrollcommand=self.scrollbar.set)
        
        self.logger.tag_configure(0, background="#27d827",foreground='#d82780')
        self.logger.tag_configure(1, background="#58a758")
        self.logger.tag_configure(2, background="#4bb543")
        self.logger.tag_configure(3, background="#000000",foreground='#00aecd')
        self.logger.tag_configure(4, background="#ffd8ff")
        self.logger.tag_configure(5, background="#ffc4ff")
        self.logger.tag_configure(6, background="#ff89ff")
        self.logger.tag_configure(7, background="#ff9d9d")
        self.logger.tag_configure(8, background="#ff6262")
        self.logger.tag_configure(9, background="#d80000",foreground='#00d8d8')

        self.framehp = Frame()

        self.framehp.place(relx=xpos,rely=0.17)        
        self.framehost=Frame(self.framehp)
        self.frameport=Frame(self.framehp)
        self.invalidtext=Label(self.framehost,text=' ✘ Please Enter a number \nfrom 0-254',foreground='#c40000')
        self.invalidtextport=Label(self.frameport,text=' ✘ Please Enter a number \nfrom 1-65535',foreground='#c40000')
        self.framehost.pack(side=TOP,anchor=W)
        self.frameport.pack(side=TOP,anchor=W)
        
        self.hostnum1=intEnt(self.framehost,width=3,label=self.invalidtext)
        self.hostnum1.insert(INSERT,'0')
        self.hostnum2=intEnt(self.framehost,width=3,label=self.invalidtext)
        self.hostnum2.insert(INSERT,'0')
        self.hostnum3=intEnt(self.framehost,width=3,label=self.invalidtext)
        self.hostnum3.insert(INSERT,'0')
        self.hostnum4=intEnt(self.framehost,width=3,label=self.invalidtext)
        self.hostnum4.insert(INSERT,'0')
        self.dot1=Label(self.framehost,text='.')
        self.dot2=Label(self.framehost,text='.')
        self.dot3=Label(self.framehost,text='.')
        
        self.hostlabel=Label(self.framehost,text='Host  :')
        
        self.portnum=intEnt(self.frameport,width=6,\
                            maxlen=5,minval=0,maxval=65536,label=self.invalidtextport)
        
        self.portlabel=Label(self.frameport,text='Port  :')

        self.portnum.insert(INSERT,'10086')
        self.hostlabel.pack(side=LEFT,pady=3)   
        self.hostnum1.pack(side=LEFT,pady=3)
        self.dot1.pack(side=LEFT,pady=3)    
        self.hostnum2.pack(side=LEFT,pady=3)
        self.dot2.pack(side=LEFT,pady=3)
        self.hostnum3.pack(side=LEFT,pady=3)
        self.dot3.pack(side=LEFT,pady=3)
        self.hostnum4.pack(side=LEFT,pady=3)
        self.portlabel.pack(side=LEFT,pady=3)
        self.portnum.pack(side=LEFT, pady=3)

        self.errhost=Label(text='Number must between 0 and 255')
        self.errport=Label(text='Number must between 1 and 65535')


        self.framets = Frame(colormap='new')
        self.framets.place(relx=xpos,rely=0.27)
        self.timespan=IntVar()
        self.scale=Scale(self.framets,variable=self.timespan, orient=HORIZONTAL, \
                         from_=10, to=60,bg='#dcdcdc', length=230)
        self.scale.set(60)
        self.tslabel=Label(self.framets,text='Time per File (seconds):')
        self.tslabel.pack(side=TOP,anchor=W)   
        self.scale.pack(side=LEFT)
        
        
        self.frame2= Frame(colormap='new')
        self.frame2.place(relx = xpos, rely = 0.5)
        self.outbtn= Button(text='Select Directory',command=self.Folder,bg='#cfcfcf',width=20)
        self.dir=os.path.join('data','')
        self.outbtn.place(relx=xpos,rely=0.4)
        self.dirlabel=Label(self.frame2,text='↓ Curret Directory ')
        self.dirtext= Label(self.frame2,text=self.dir,wraplength=400,justify=LEFT)
        self.dirlabel.pack(side=TOP,anchor=W,pady=5)
        self.dirtext.pack(side=LEFT)
        
        self.radioframe= Frame(colormap='new')
        self.v = BooleanVar()
        explain=Label(self.radioframe,text='Save File As: ').pack(side=LEFT,anchor=W)
        self.rb1=Radiobutton(self.radioframe, text=".mseed", variable=self.v, value=False)
        self.rb1.pack(side=LEFT,anchor=W)
        self.rb2=Radiobutton(self.radioframe, text=".dat", variable=self.v, value=True)
        self.rb2.pack(side=LEFT,anchor=W)
        
        self.radioframe.place(relx = xpos, rely = 0.45)
        self.sendbutton.pack(side=RIGHT,anchor=SE,padx=20, pady=10, expand=YES)
        self.addrlabel.pack(side=TOP,anchor=NW)
        self.cliententry.pack(side=TOP,anchor=NW)
        self.commandlabel.pack(side=TOP,anchor=NW)
        self.commandtext.pack(side=TOP,anchor=NW)
        self.bytestosend=bytearray(b'') 
       
        self.selectedbox=None
        self.desiredbox=None
        self.headlen=24
        self.commandlist={'command1':b'\x55\xaa\x55','command2':b'\xaa\x55\xaa'}
        return
    
    def send_command(self):
        
        
        box=self.cliententry.get()
        self.tgtbox=box
        self.showtext('{} Command send to Box# {}'.format(self.commandtext.get(),box),2)
        return        
    
    def check_entval(self):
        
        self.hostcheck=all((self.hostnum1.check(),self.hostnum2.check(),\
                            self.hostnum3.check(),self.hostnum4.check()))
        self.portcheck=self.portnum.check()
        
        if self.hostcheck:
            self.errhost.place(relx=0.4,rely=0.4)
        else:
            self.errhost.place_forget()
        if self.portcheck:
            self.errport.place(relx=0.4,rely=0.4)
        else:
            self.errport.place_forget()
        return
        
        
    def socket_thread(self):
        
        host=self.check_ip()
        port=self.check_port()
        if (host and port):
            
            self.showtext ("thread started.. ",0)
            self.ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.ls.bind((host, port))
                
            except OSError as err:
                self.enableedit()
                self.showtext ("OS error: {0} ".format(err),9)
                self.showtext ('Please Close Application using Port: %s ' %port,9)
                self.showtext ('Server Stopped ',7)
                self.connectionl.configure(text="OFF.",bg='#ff5f5f')
                raise OSError ('Port Being Used')
                return
                
            self.running = 1
            sleep(0.2)
            
            try:
                self.showtext("Server listening on port %s " %port,1)
                while self.running != 0:            
                    self.ls.listen(5)
                    self.ls.setblocking(1)
                    self.connectionl.configure(text="RUNNING!",bg='#4bb543')
                    (conn, addr) = self.ls.accept()
                    self.showtext("client is at "+ str(addr[0])+ \
                                       " on port "+str(addr[1]),2)
                    newthread = Thread(target=self.run_server, args=(conn,addr))
                    newthread.start()
                    newthread.join(1)
                

                                                        
            except (Exception) as e:
                self.enableedit()
                self.showtext("Connect exception: "+str(e) +'',9)
                self.connectionl.configure(text="OFF.",bg='#ff5f5f')
                self.forcestop()
                return
    
        return            
    
    def run_server(self,conn,addr):
        head=b'\x34\x37\x36\x35'
        NotInserted=True
        i=0
        counter=0
        data_saved=bytearray(b'')
        seed_data=[]


        recv_data=bytearray(b'')
        data_recv=bytearray(b'')
        timeNotpresent=True
        SendClientInfo=False
        st=Stream([])


        self.showtext("connected to {}, {}".format(conn,addr),3)
        self.showtext('Data From: {}'.format(addr),3)
        
        try:
            
            while self.running !=0:

                recv_data = bytearray(conn.recv(524288))
                Permission=False
                data_recv += recv_data
                                
                if len(data_recv)>=15000:
                    

                    start=data_recv.find(b'\x32\x34\x56\x67')
                    end=data_recv.rfind(b'\x32\x34\x56\x67')
                    check=(len(data_recv[start:end])-self.headlen)% 4
                
                    if start==end:
        
                        data_recv=data_recv[start:]
        
                        
                    elif end > start and (check) % 4 == 0:
        
                        data_buffer=data_recv[start:end]
                        data_recv=data_recv[end:]
                        Permission=True
        
                        
                    elif end > start:
        
                        data_buffer=data_recv[start:end-check]
                        data_recv=data_recv[end:]
                        Permission=True
     
            
                if (Permission and len(data_buffer)>12):

                    connect_start=time()  # reset timeout time

                    if i==0:
                        i+=1
                        data_buffer.clear()
                        Permission=False
                        continue
                    
                        
                    ID=str(data_buffer[4:7].decode())
                    
                    if (ID=='SEL'):
                        
                                                   
                        children=self.clidisp.get_children()
                        # self.values=b'\xff\xfe\xfd\xfc\xfb'
                        self.values=bytearray(b'')
                        
                        for child in children:   
                            a=list(self.clidisp.item(child).values())
                            a=a[2][0]                                
                            if isinstance (a,int):
                                thing=struct.pack('>H',a)
                                self.values+=thing

                        conn.sendall(self.bytestosend+head+self.values)
                        # self.bytestosend.clear()
                        self.bytestosend=bytearray(b'')     
                         
                        if NotInserted:
                            address=('{}:{}'.format(addr[0],addr[1]))
                            self.clidisp.insert('', 'end','box'+ID,values=(ID,address))
    #                        self.clientnum.config(text=str(len(self.clidisp.get_children())))
                            NotInserted=False   
                        
                        if (data_buffer[7:9]!=b'\x99\x99'):
                            self.desiredbox=struct.unpack('>H',data_buffer[7:9])[0]

                    else:
                        # conn.settimeout(120)
                        conn.sendall(data_buffer[0:7])
                    
#                       print(data_buffer[0:7])
                        
                        if int(ID)==self.desiredbox:
                            self.bytestosend.clear()
                            self.bytestosend+=data_buffer
                            
                        if (self.tgtbox==ID):
                            
                            command=self.commandtext.get()
                            commandtosend=self.commandlist[command]
                            conn.sendall(commandtosend)
                            counter+=1
                            
                            if counter >= 5:
                                self.tgtbox=None
                                continue
                            if counter > 10:
                                self.tgtbox=None
                                break
                            
    
                                
                        if NotInserted:
                            address=('{}:{}'.format(addr[0],addr[1]))
                            try:
                                self.clidisp.insert('', 'end','box{}'.format(ID),values=(ID,address))
                            except:
                                pass
    #                        self.clientnum.config(text=str(len(self.clidisp.get_children())))
                            NotInserted=False
                            self.showtext('Hello, I am Box# {}'.format(ID), 2)
                        self.checkcolor()
                        if timeNotpresent:
                            try: 
                                year=struct.unpack('>1H',data_buffer[7:9])
                                year=int(year[0])
                                month=int(struct.unpack('>1B',data_buffer[9:10])[0])
                                day=int(struct.unpack('>1B',data_buffer[10:11])[0])
                                hour=int(struct.unpack('>1B',data_buffer[11:12])[0])
                                minute=int(struct.unpack('>1B',data_buffer[12:13])[0])
                                second=int(struct.unpack('>1B',data_buffer[13:14])[0])
                                starttime=datetime(year,month,day,hour,minute,second)   
        
                            except:
                                self.showtext('Invalid Time in box# {}.. Using Computer UTC\
                                                time instead'.format(ID), 7)
                                starttime=datetime.utcnow()      
                                timeNotpresent=False

        
                        data_buffer=bytearray(data_buffer[self.headlen:])
                        
                        if self.v.get():
                            if timeNotpresent:
                                fn=starttime.strftime("%Y%m%d%H%M%Ss")
                                timeNotpresent=False
                                
                            data_saved+=data_buffer 
                            
                            if len (data_saved) >=12000*self.timespan.get():
    #                            self.showtext('Time Check--> '+str(starttime),2,self.debug.get())
                                self.showtext('{} Writing Original Files'.format(addr),2,self.debug.get())
                                with open (os.path.join(self.dir,str(ID),fn+'.dat'),'wb') as f:
                                    f.write(data_saved)
                                data_saved.clear()
                                timeNotpresent=True
                            
                        else:

                            unpacked_display_data = np.array(unpack(data_buffer))
                            if max(unpacked_display_data) > 10e10:
                                data_buffer.clear()
                                Permission=False   
                                self.showtext('Box {} Have corrupted Data'.format(ID),7)
                                seed_data.extend(np.zeros(len(unpacked_display_data)))                                    
                                continue 
                            
                            # seed_data.extend(unpacked_display_data)
                            
                            # if len(seed_data) >=3000*self.timespan.get():
                            #     self.showtext('{} Writing miniseed Files'.format(addr),2,self.debug.get())
                            #     writeseed(np.array(seed_data[:3000*self.timespan.get()]),\
                            #               starttime,ID,self.dir)
                            #     seed_data=seed_data[3000*self.timespan.get():]
                            #     timeNotpresent=True
        
                            tempst=trace_gen(unpacked_display_data,\
                                              starttime,ID)

                            st+=tempst

                            if (len(st)>=int(3*self.timespan.get())):
        
                                self.showtext('{} Writing mini-seed Files'.format(addr),2,self.debug.get())
                                st.merge(method=1,fill_value='interpolate')
                                # st.merge(method=-1)
                                writestream(st,ID,self.dir)
                                st=Stream([])

                        


                 
                    data_buffer.clear()
                    Permission=False                                       


                    if (self.running==0) or (time()-connect_start > 60):
                        self.showtext ("No Data! Closing Connections!",9)
                        # self.clidisp.delete('box'+str(ID))
                        break
                                        
                
        except (Exception) as e:
            # we can wait on the line if desired
            self.showtext ("socket error: "+repr(e),9)  

                      
            
    
        finally:
            
            self.showtext ("Client at {} disconnected...".format(addr),3)
            SendClientInfo=False
            try:
                self.clidisp.delete('box{}'.format(ID))
                conn.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.showtext ("closing connection on Box# {}".format(ID),5)
            conn.close()
            self.showtext ("connection closed on Box# {}".format(ID),4)
            self.tgtbox=None
            counter=0            
            self.checkcolor()
            return
        
        
    def close_sequence(self,conn,addr,ID=None):
        
        try:
            self.clidisp.delete('box{}'.format(ID))
            self.forcestop()
        except:
            pass
        
        self.checkcolor()
        return        
        
    def startc(self):

        
        if self.running == 0:
            
            self.disableedit()
            self.connectionl.configure(text="INITIALIZING!",bg='#ffffaa')
            self.size=1000*3*int(self.timespan.get())
            self.scale.config(state='disabled',bg='#3f3f3f',fg='#fafafa')
            self.showtext ("Starting Server ",0)
            self.thread=Thread(target=self.socket_thread)
            self.thread.start()
            
            self.startb.configure(bg='#ff276f',text = "Stop Server",command=self.stopc)

        
        else:
            self.showtext ("Server already started. ",8)
            return
        return
            
            
    def stopc(self):

        self.enableedit()
        self.scale.config(state='active',bg='#dcdcdc',fg='#000000')
    
        if self.running:
            self.forcestop(Close=True)
            self.showtext ("stopping thread... ",7)
            sleep(1)
            self.clidisp.delete(*self.clidisp.get_children())
            self.checkcolor()
            self.connectionl.configure(text="OFF.",bg='#ff5f5f')
            self.running = 0
            self.thread.join(1)


        try:
            raise KeyboardInterrupt ('Server Terminated Due to user Action')
        except KeyboardInterrupt:
            self.showtext('Server Terminated Due to user Action',7)
            return          
        else:
            self.showtext ("Server not running",7)   
        return            

    def check_ip(self):
        
        try:
            if int(self.hostnum1.get())>255:
                showerror("Error","First number in your Host Section is greather than 255 " )
                self.showtext('Server Stopped ',7)
                return 0
            elif int(self.hostnum2.get())>255:
                showerror("Error","Second number in your Host Section is greather than 255 " )
                self.showtext('Server Stopped ',7)
                return 0
            
            elif int(self.hostnum3.get())>255:
                showerror("Error","Third number in your Host Section is greather than 255 " )   
                self.showtext('Server Stopped ',7)
                return 0
            
            elif int(self.hostnum4.get())>255:
                
                showerror("Error","Forth number in your Host Section is greather than 255 " ) 
                self.showtext('Server Stopped ',7)
                return 0
            
            else: 
                return '{}.{}.{}.{}'.format (self.hostnum1.get(),self.hostnum2.get(),\
                  self.hostnum3.get(),self.hostnum4.get())
        except:
            showerror("Error","Please make sure whole numbers are entered in host section" ) 
            self.showtext('Server Stopped ',7)
            return 0
                
    def check_port(self):
        
        
            try:
                
                if 65536<int(self.portnum.get()):         
                    
                    showerror("Error","Please enter a whole number between 1 and 65535 in Port section" )
                    self.showtext('Server Stopped ',7)
                else:
                    return int(self.portnum.get())
                
            except:
                
                showerror("Error","Please make sure whole numbers are entered in port section" ) 
                self.showtext('Server Stopped ',7)
                
                return 0


                
    
    def Folder(self):
        
        targetdir=askdirectory()
        
        if targetdir:
            self.dirtext.config(text=targetdir)
            self.dir=targetdir
        return
    
    def checkcolor(self):
        
        if len(self.clidisp.get_children())>0:
            
            self.numtitle.config(text='Total Connected Clients: ',\
                        bg='#afffbf')
    
            self.clientnum.config(text=str(len(self.clidisp.get_children())),\
                         bg='#afffbf',font=("", 16)) 
        else:
            
            self.numtitle.config(text='Total Connected Clients: ',\
                        bg='#ff5f5f')
    
            self.clientnum.config(text=str(len(self.clidisp.get_children())),\
                         bg='#ff5f5f',font=("", 16)) 
        return
    
    def placeframe(self):

        if self.expertmode.get():
            showwarning("Warning","Command in Expert Mode can permnantly " \
                               'shutdown selected device(s)')
            self.framecommand.place(relx=0.05,rely=0.79)
            
        else:
            
            self.framecommand.place_forget()
            
        return
        
    def showtext(self,text,colorcheck,DEBUG=True):
        
        with open ('logs.txt','a+') as f:
            f.write(gettime()+text+'\n')
            
        if DEBUG:
            self.logger.config(state=NORMAL)
            self.logger.insert(END,gettime()+text+'\n',colorcheck)
            self.logger.see('end')
            self.logger.config(state=DISABLED)
            return
        return
        
        
    def forcestop(self,Close=False):
        self.startb.configure(bg='#90ee90',text = "Start Server",command=self.startc)
        try:
            self.ls.shutdown(socket.SHUT_RDWR)
        except:
            pass
        if Close:
            try:
                self.ls.close()
            except:
                pass
        return
        
    def enableedit(self):
        
        self.portnum.configure(state='normal')
        self.hostnum1.configure(state='normal')
        self.hostnum2.configure(state='normal')
        self.hostnum3.configure(state='normal')
        self.hostnum4.configure(state='normal')
        self.rb1.configure(state='normal')
        self.rb2.configure(state='normal')
        self.outbtn.configure(state='normal')
        return
    
    def disableedit(self):
        
        self.portnum.configure(state='disable')
        self.hostnum1.configure(state='disable')
        self.hostnum2.configure(state='disable')
        self.hostnum3.configure(state='disable')
        self.hostnum4.configure(state='disable')
        self.rb1.configure(state='disable')
        self.rb2.configure(state='disable')
        self.outbtn.configure(state='disable')        
        return
            
class intEnt(Entry):
    __slots__=('canvas','label','minval','maxval')
    def __init__(self, master=None, maxlen=3,minval=-1,maxval=255,label=None,**kwargs):
        self.var = StringVar()
        self.maxlen=maxlen
        self.minval=minval
        self.maxval=maxval
        
        self.canvas=Canvas(width=250, height=180)
        self.label=label
#        self.label = Label(self.framehp,text=' ✘ Invalid Input',foreground='#ff0000')
        Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.old_value = ''
        self.var.trace('w', self.check)
        self.get, self.set = self.var.get, self.var.set
        self.config(bg='#ffffff')
        return
    
    def check(self, *args):
        if self.get().isdigit(): 

            # the current value is only digits; allow this
            if len(self.get())<=self.maxlen:
                
                self.old_value = self.get()
                self.config(bg='#ffffff')    
                self.label.pack_forget()
                self.canvas.place_forget()
                

                if not(self.minval<int(self.get())<self.maxval):
                    self.set(self.old_value)
                    self.config(bg='#ff6f6f')                    
                    self.label.pack(side=RIGHT,anchor=E)
                    self.canvas.create_rectangle(0,0,240,180)
                    self.canvas.place(relx=0.05,rely=0.65)

                    
                            
            else:
                self.set(self.old_value)


                
                        
        elif not(any(self.get())):
            self.old_value = self.get()
            self.config(bg='#ff6f6f')
            self.label.pack(side=RIGHT,anchor=E)
            self.canvas.create_rectangle(0,0,240,180)
            self.canvas.place(relx=0.05,rely=0.65)


        
  

        else:
            # there's non-digit characters in the input; reject this 
            self.set(self.old_value)
            self.config(bg='#ff6f6f')
            self.label.pack(side=RIGHT,anchor=E)
            self.canvas.create_rectangle(0,0,240,180)
            self.canvas.place(relx=0.05,rely=0.65)

        return



            

                        
#try:
root = Tk()
root.title("My Server")
root.geometry('1280x720')
root.option_add("*Font", "12")
gui = Gui(root)
root.mainloop()
    
#finally:
#    gui.forcestop(Close=True)
#    sys.exit()







