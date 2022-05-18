from pprint import isreadable
import numpy as np
from queue import Queue
import threading
# A file source processor. It assambles file open and close operations, defines a function to read in data
# and provides a way to put data into a shared queue 
class FileSourceProcessor:
    def __init__(self,filename,datatype:np.dtype,databuffer:Queue) -> None:
        self.__filename=filename
        self.__data_type=datatype
        self.__target_buffer=databuffer       
        self.__my_buffer=Queue(1e6)
        self.__fid=open(self.__filename,'rb')
        pass

    # read in certain number of samples and return the data & if enough data read
    def read_data(self,num_of_samples):
        data=np.fromfile(self.__fid,self.__data_type,num_of_samples)
        sample_read=len(data)
        is_read=True
        if(sample_read!=num_of_samples):
            is_read=False
            print("unable to read enough samples, target sample: %d, but read: %d"%(num_of_samples,sample_read))
        return data,is_read
        pass


    # put all the data into the shared queue
    def push_to_buffer(self,data:np.array):
        for item in data:
            self.__target_buffer.put(item=item)


    def __del__(self):
        self.__fid.close()
        print("The file processor ends its life\n")


# A subclass of threading.Thread. This class makes the file source processor a thread 
class FileSourceThread (threading.Thread):
    def __init__(self, threadID, name, filename,datatype,buffer):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.filename=filename
        self.__file_processor=FileSourceProcessor(self.filename,datatype,buffer)
    def run(self):
        print ("开始线程：" + self.name)
        is_enouth=True
        while(is_enouth):
            #read in data, and confine the maximun number of samples to be read in
            [data,is_enouth]=self.__file_processor.read_data(100)
            #push the data into a buffer
            self.__file_processor.push_to_buffer(data)
        print ("退出线程：" + self.name)