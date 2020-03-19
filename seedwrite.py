import numpy as np
from obspy import Trace, Stream
from datetime import datetime
import os
import sys

##TODO: get a more precesice timing with generating streams on every data send and write miniseed files.

def trace_gen(data_in,starttime,ID):
    
    crit=len(data_in) % 3
    
    if  crit != 0:
        data_in=data_in[0:len(data_in)-crit]
#    print(data_in)
    data_in = np.ascontiguousarray(data_in)
    data_in=data_in.reshape(-1,3).T
    
    stats = {'network': '111', 'station': ID, 'location': '',
             'channel': '1', 'npts': len(data_in[0]), 'sampling_rate': 10,
             }
    stats2 = {'network': '111', 'station': ID, 'location': '',
             'channel': '2', 'npts': len(data_in[1]), 'sampling_rate': 10,
             }
    stats3 = {'network': '111', 'station': ID, 'location': '',
             'channel': '3', 'npts': len(data_in[2]), 'sampling_rate': 10,
             }
    
    
    # set current time
    stats['starttime'] = starttime
    stats2['starttime'] = starttime
    stats3['starttime'] = starttime


    tr = [Trace(data=data_in[0], header=stats), \
                 Trace(data=data_in[1], header=stats2), \
                 Trace(data=data_in[2], header=stats3)]
    return tr

def writestream(stream_in,ID,directory):
    # Create directory
    dirName = os.path.join(directory,ID)

#    print(data_in)
    # Create target Directory if don't exist
    if not os.path.exists(dirName):
        if not os.path.exists(directory):
            os.mkdir(directory)
        os.mkdir(dirName)
#        print("Directory " , dirName ,  " Created ")
        
    path=os.path.join(dirName,'')
    fn=stream_in[0].times("utcdatetime")
    fn=fn[0]
    fn=fn.strftime("%Y%m%d%H%M%S")
    stream_in.write(os.path.join(path,fn+".mseed"), format='MSEED')
    #stream_in.astype('float32').tofile(os.path.join(path,fn+".dat"))
    
    return

    
    
def writeseed(data_in,starttime,ID,directory='.',fileName=None):

    
    # Create directory
    dirName = os.path.join(directory,ID)

#    print(data_in)
    # Create target Directory if don't exist
    if not os.path.exists(dirName):
        if not os.path.exists(directory):
            os.mkdir(directory)
        os.mkdir(dirName)
#        print("Directory " , dirName ,  " Created ")
        
    path=os.path.join(dirName,'')
    # Convert to NumPy character array
#    data = np.fromstring(data, dtype='|S1')
    
    # Fill header attributes
    crit=len(data_in) % 3
    
    if  crit != 0:
        data_in=data_in[0:len(data_in)-crit]
        
    data_in = np.ascontiguousarray(data_in)
    
    data_in=data_in.reshape(-1,3).T
    
    stats = {'network': '111', 'station': ID, 'location': '',
             'channel': '1', 'npts': len(data_in[0]), 'sampling_rate': 10,
             }
    stats2 = {'network': '111', 'station': ID, 'location': '',
             'channel': '2', 'npts': len(data_in[1]), 'sampling_rate': 10,
             }
    stats3 = {'network': '111', 'station': ID, 'location': '',
             'channel': '3', 'npts': len(data_in[2]), 'sampling_rate': 10,
             }
    
    
    
    # set current time
    stats['starttime'] = starttime
    stats2['starttime'] = starttime
    stats3['starttime'] = starttime


    st = Stream([Trace(data=data_in[0], header=stats), \
                 Trace(data=data_in[1], header=stats2), \
                 Trace(data=data_in[2], header=stats3)])

    # write as ASCII file (encoding=4)
    if fileName:
        fn=fileName
    else:
        fn=stats['starttime'].strftime("%Y%m%d%H%M%Ss")
        fn=fn.replace('-','_')
        fn=fn.replace(':','_')
        fn=fn.replace('.','s')
        
    st.write(os.path.join(path,fn+".mseed"), format='MSEED')
    

    return

def readdat(file):    
    if file.endswith('.DAT') or file.endswith('.dat'): 
        data=np.fromfile(file,np.float32)    
        starttime=file.split('.')[0]
        
        if sys.platform.startswith('win'):
            starttime=starttime.split(r'\\')[-1]
        else:
            starttime=starttime.split(r'/')[-1]

        if len(starttime)==14: 
            year=int(starttime[0:4])
            month=int(starttime[4:6])
            day=int(starttime[6:8])
            hour=int(starttime[8:10])
            minute=int(starttime[10:12])
            second=int(starttime[12:])
            starttime=datetime(year,month,day,hour,minute,second)
        else:
            return 0
        

    else:
        return 0

    return (data,starttime)



        
        
        
        
        
        
