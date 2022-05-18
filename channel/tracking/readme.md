# Tracking

Tracking generates local spreading code and carrier to despread signals based on initial estimation of code phase, frequency, carrier phase and frequency from acqusition.

## TrackThread

TrackThread is the encapsulation of trackors. A TrackThread does the following things:

When the channel gets the initial estimation from aqusition, the TrackThread starts initialization. The chosen "trackor" must defined during the initialization. The initial state of code phase, frequency, carrier phase & frequency must be passed to the tracker when it is defined. 

After initiation, this thread starts to run the tracking process to process input signal data and produces the despreaded signal and estimation of data quality as output.

## Trackors

Different trackers follows different principles with different implemention. However, all trackors must have 3 functions:

1. \_\_init__: initialize a trackor. **Required parameters**: prn, code length, initial state, source buffer, result buffer. **Optional parameters**: ms to process (total length of processing), accumulation time (some trackors may decide it by itself)

2. set_init_state: Reset the initial state. This will be used after losing lock and a sucessful reaqusition. 

3. track_process: The main funciton that gets raw data and conduct signal processing. It is the function runs in TrackThread "run" function.

