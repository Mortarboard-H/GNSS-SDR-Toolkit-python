# Acquisition

## what does acquisition do?

Acquisition acquires examines the signal to check if it contains the signal of the certain satellite. 

It accepts data streams as input and produces the estimiation of code phase and carrier frequency as outputs.

To implement acquisition function, we use 'acquisition_thread.py' and 'acqusitions.py' to contain the definition of acquisition thread and the avaliable acquisitons algorithms.

## acquisition_thread

It defines the thread to be used when one wants to set up a channel.

This thread accepts data from a shared queue (shared with tracking thread) containing the intermediate signal (in MHz).

So this thread will compete with tracking thread and only runs when tracking thread is stopped.

A thread must declare what acquisition method to be used and the parameters of the chosen method 

A thread also must produce a flag, indicating whether successful or not, and the estimation of code phase and carrier frequency if successful.

## acquisitions

A file or module stores all the acquisition methods

### GPS_L1_PCPA_1ms

A class of parallel code phase acquisition method with 1ms for GPS L1 signal. 