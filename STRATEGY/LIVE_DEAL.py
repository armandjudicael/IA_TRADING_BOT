from iqoptionapi.stable_api import IQ_Option
import logging
import time

#logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')
EMAIL = "voahanginirina.noelline@gmail.com"
PASSWORD = "Noel!ne1969"
Iq=IQ_Option(EMAIL,PASSWORD)
Iq.connect()#connect to iqoption
while_run_time=10
#For binary option

name="live-deal-binary-option-placed"
active="NZDUSD-OTC"
_type="binary"#"turbo"/"binary"
buffersize=20#
print("_____________subscribe_live_deal_______________")
Iq.subscribe_live_deal(name,active,_type,buffersize)

start_t=time.time()
while True:
    #data size is below buffersize
    #data[0] is the last data
    data=(Iq.get_live_deal(name,active,_type))
    print("__For_binary_option__ data size:"+str(len(data)))
    print(data)
    print("\n\n")
    time.sleep(1)
    if time.time()-start_t>while_run_time:
        break
print("_____________unscribe_live_deal_______________")
Iq.unscribe_live_deal(name,active,_type)