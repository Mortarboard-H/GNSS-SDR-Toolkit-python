# Channel

The basic unit of processing a satellite

# What does channel do?

Channel functions as a controlling unit of a signal processing of a satellite. It controls the acquistion thread, tracking thread and decoding thread of a satellite's signal. 

# How does it controll the process?

Before the estabilishment of a channel of a certain satellite. The channel first run the acqusition thread to see if there is the signal of the certain satellite. 

Here comes two situations: 1. **no such satellite** 2. **find the signal**

In **situation 1: no such satellite.** The channel tries several times of acquisiton and if still unable to find the signal. The channel reports to a higher level controller "my signal can not be found, please close my channel". THe higher level controller should **kill** the channel and  decides when to reopen this channel.

In **situation 2: find the signal.** The channel kills its acquisiton thread and starts its tracking thread and decoding thread. The channel will monitor the quality of signal of itself, where two states may occur: **good state** and **bad state**. 

**Good state**: The carrier to noise ratio is good and the decoded signal is clear enough to be writen to ephemeris files. The channel keeps running without extra behaviour.

**Bad state**: The carrier to noise ratio is bad and the decoded signal is not clear, or the tracking loop is totally unable to lock the signal. Then the channel will suspend itself. It will restart its acqusition several times to decide its situation. 
