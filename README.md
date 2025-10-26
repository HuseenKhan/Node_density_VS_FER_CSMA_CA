# A Python code to study the impact of density of network density on node's FER. 

# Introduction
This project analyzes how node density impacts the collision rate in CSMA/CA-based networks. Although CSMA/CA operates on a listen-before-talk mechanism, collisions still occur in IEEE 802.11 networks, which can significantly reduce the overall network throughput.
In this project, the assumption is made that all nodes can sense each other, the network is saturated and MCS is fixed (i.e., no Rate Adaptation algorithm). Under such conditions, collisions primarily occur when two or more nodes select the same backoff value. As the number of nodes in the network increases, the probability of two nodes selecting the same backoff value also increases, resulting in a higher collision rate.



# Usage
Simply run the Node_Density_VS_FER_CSMA_CA.py file.
The program will prompt you to enter the following inputs:

Number of nodes in the network

Frame transmission time (in time slots)

Simulation time (in time slots)

Note: The duration of one time slot is 10 µs.

Example:

![User Input](user_input.png)

At the end of the simulation, the terminal displays the performance of each node.

![Simulation Result](simulation_result.png)





