import time
import random
import numpy as np
import pandas as pd

idle_slots = 0
busy_slots = 0
channel_energy=-100
shared_channel_status = "Idle"


class Buffer:
    def __init__(self):
        self.frames = [1]  # Initially the buffer contains one frame

    def has_frames(self):
        return len(self.frames) > 0

    def get_frame(self):
        return self.frames.pop(0)

    def add_frame(self):
        self.frames.append(1)

class WLANNode:
    time_slot=0
    CW_min=0
    CW_max=31

    def __init__(self, node_id,transmission_slots):
        self.node_id = node_id
        self.backoff_time = 0
        self.decrement_difs_count = 0
        self.deffer = 5
        self.state = "DIFS"
        self.txop = 0
        self.successful_transmission = 0
        self.collision = 0
        self.retry = 0
        self.transmitting_nodes = []
        self.collision_occurred = False
        self.retry_occurred = False
        self.buffer = Buffer()
        self.CW_current = self.CW_max
        self.time_slot = 0
        self.slot_counter = 0
        self.channel_state = "Idle"
        self.transmission_slots = transmission_slots
        self.original_transmission_slots = transmission_slots
        self.frame_dropped = 0
        self.transmission_count = 0
        self.unsucessful_attempt = 0
        self.consecutive_unsucessful_attempt = 0
        self.CST = -82  # dBm
        self.sensing_nodes = []
        self.prev_channel_state = self.channel_state
        self.channel_energy = -95
        self.recive_energy = None

        self.statistics = {}
        self.deffer_slots = 0
        self.backoff_slots = 0
        self.transmission_frame_slots = 0




    def set_state(self, state):
        self.state = state

    def decrement_difs(self):
        if self.deffer > 0:
            self.deffer -= 1
            #print(f"Node {self.node_id}: Performing DIFS {self.deffer}")
            self.deffer_slots += 1
            if self.deffer == 0:
                self.decrement_difs_count += 1
                self.set_state("Perform carrier sense")
                self.generate_backoff()

    def set_backoff_time(self, time):
        self.backoff_time = time


    def generate_backoff(self):
        if self.state == "Perform carrier sense" and self.channel_state == "Idle" and self.backoff_time == 0:
            self.set_backoff_time(np.random.randint(self.CW_min, self.CW_current))
            print(f"Node {self.node_id}: Generated backoff value: {self.backoff_time} time units")

            self.set_state("Backoff")
            if self.backoff_time == 0:
                self.txop += 1
                self.state = "Transmit"
        else:
            self.state = "Backoff"
            print(f"Node {self.node_id}: backoff value: {self.backoff_time} time units")


    def decrement_backoff(self):
        if self.state != "Backoff":
            return
        if self.channel_state == "Idle":
            if self.backoff_time > 0:
                self.backoff_time -= 1
                self.backoff_slots += 1
            if self.backoff_time == 0:
                self.txop += 1
                self.state = "Transmit"
        else:
            # frozen, do nothing this slot
            pass

    def drop_frame_and_reset(self):
        print(f"Node {self.node_id}: Frame dropped after 6 retries. Resetting contention window size...")
        self.buffer.get_frame()  # Remove the frame from buffer
        self.CW_current = 31  # Reset contention window size

        self.retry = 0

    def transmitting_frame(self,):
        transmitting_nodes = []  # List to store nodes currently in "Transmit" state



        for node in nodes:
            if node.state == "Transmit":
                transmitting_nodes.append(node)

        if shared_channel_status == "Busy":
            self.slot_counter += 1
            if self.slot_counter == 1:
                print(
                    f"Node {self.node_id}: Transmitting data... Remaining transmission slots: {self.transmission_slots}")
            if self.slot_counter == 2:
                if self.transmission_slots > 0 :
                    self.transmission_slots -= 1
                    self.transmission_count += 1
                self.slot_counter = 0
                print(
                    f"Node {self.node_id}: Transmitting data... Remaining transmission slots: {self.transmission_slots}")

                if len(transmitting_nodes) > 1:  # More than one node transmitting at the same time, i.e., collision
                    self.collision_occurred = True

                    print(f"Node {self.node_id}: Detected a possible collision with Node(s) {', '.join(str(node.node_id) for node in transmitting_nodes if node.node_id != self.node_id)}")

            if self.transmission_slots == 0:
                if self.collision_occurred:
                    print(
                        f"Node {self.node_id}: Transmission failed due to earlier collision. Preparing to re-transmit the frame...")
                    self.collision += 1
                    self.collision_occurred = False
                    self.retry += 1
                    print(
                        f"Node {self.node_id} has { self.retry} retransmission")
                    self.CW_current = (2 * self.CW_current)+1
                    print("The maximum contention window size is", self.CW_current)
                    if self.retry >= 6:  # Drop the frame after 6 retries
                        self.frame_dropped+=1
                        self.drop_frame_and_reset()
                        self.buffer.add_frame()

                else:

                    print(f"Node {self.node_id}: Successfully transmitted the frame")
                    self.successful_transmission += 1
                    self.buffer.get_frame()  # Remove transmitted frame from buffer
                    self.buffer.add_frame()  # Add a new frame to buffer
                    self.CW_current = 31

                self.set_state("DIFS")
                self.deffer=5
                self.transmission_slots = self.original_transmission_slots

    def update_channel_state(self, channel_energy):
        # Decide Busy vs Idle based only on sensed transmitters and CST
        sensed_tx = any(n.state == "Transmit" for n in self.sensing_nodes)
        if self.state == "Transmit":
            new_state = "MAC Off"  # local MAC is off during own TX
        else:
            new_state = "Busy" if (sensed_tx and self.CST < channel_energy) else "Idle"

        # Handle Busy -> Idle handover for DCF correctly
        if self.prev_channel_state in ["Busy", "MAC Off"] and new_state == "Idle":
            # Only insert a single DIFS if we were frozen and not already in DIFS
            if self.state in ["Backoff", "Perform carrier sense"]:
                self.set_state("DIFS")
                self.deffer = 5

        self.channel_state = new_state
        self.prev_channel_state = new_state

    def set_sensing_nodes(self, nodes):
        self.sensing_nodes = nodes

    @classmethod
    def update_channel_status(cls, status):
        cls.channel_status = status


    def get_node_state(self):
        return self.state

    def __str__(self):
        return f"Node ID: {self.node_id}, State: {self.state}, Backoff Time: {self.backoff_time}, Transmission Slots: {self.transmission_slots}"

# ====== USER INPUT SECTION ======

def get_int(prompt):
    """Helper function to safely get a positive integer input from the user."""
    while True:
        try:
            value = int(input(prompt))
            if value <= 0:
                print("Value must be greater than zero.")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer.")

# Collect all user inputs
num_nodes = get_int("Enter Number of nodes in the network: ")
tx_slots = get_int("Enter Frame Transmission Time: ")
time_slots = get_int("Enter Total Simulation time: ")

# =================================


# =================================

# Generate node IDs dynamically
node_ids = [f"AP{i}" for i in range(1, num_nodes + 1)]

# Create WLANNode instances
nodes = [WLANNode(node_id, tx_slots) for node_id in node_ids]


sensing_matrix = np.ones((num_nodes, num_nodes), dtype=int)
np.fill_diagonal(sensing_matrix, 0)
sensing_matrix = sensing_matrix.tolist()

# Set sensing nodes for each node
for i in range(len(nodes)):
    sensing_nodes_for_i = []
    for j in range(len(nodes)):
        if sensing_matrix[i][j] == 1:
            sensing_nodes_for_i.append(nodes[j])
    nodes[i].set_sensing_nodes(sensing_nodes_for_i)

# Print sensing relationships
for node in nodes:
    sensing_names = [n.node_id for n in node.sensing_nodes]
    print(f"{node.node_id} can sense: {', '.join(sensing_names) if sensing_names else 'None'}")

system_states = []
transmission_opportunities_data = []

for slot in range(time_slots):

    print(f"\nTime Slot: {slot}")

    previous_channel_status = shared_channel_status
    if any(node.state == "Transmit" for node in nodes):
        channel_energy = -40
        shared_channel_status = "Busy"
        busy_slots += 1
    else:
        shared_channel_status = "Idle"
        channel_energy = -100
        idle_slots += 1
    #calculate_distances(nodes)

    transmitting_nodes = [node for node in nodes if node.state == "Transmit"]
    print(f"Number of transmitting nodes at time slot {slot}: {len(transmitting_nodes)}")
    for node in nodes:
        node.update_channel_state(channel_energy)
    system_state = []  # Store state of each node in the system state
    for node in nodes:
            system_state.append(node.get_node_state())

    system_states.append(system_state)
    channel_status = "Idle" if shared_channel_status == "Idle" else f"Busy (Node {', '.join(str(node.node_id) for node in nodes if node.state == 'Transmit')})"
    print(f"Channel Status: {channel_status} - node State: {system_state}")


    for node in nodes:
        if node.state == "DIFS":
            node.decrement_difs()
        elif node.state == "Perform carrier sense":
            node.generate_backoff()
        elif node.state == "Backoff":
            node.decrement_backoff()
        elif node.state == "Transmit":
            node.transmitting_frame()


total_txop = [node.txop for node in nodes]
total_decrement_difs_count = [node.decrement_difs_count for node in nodes]

total_successful_transmission = [node.successful_transmission for node in nodes]
total_collision = [node.collision for node in nodes]
# Calculate total transmission opportunities
total_transmission_opportunities = sum(node.txop for node in nodes)
# ====== END-OF-SIMULATION SUMMARY ======
print("\n=== Simulation Summary ===")
for node in nodes:
    fer = (node.collision / node.txop * 100) if node.txop > 0 else 0.0
    print(f"{node.node_id}: Average Collision rate = {fer:.2f}% | Successful Transmissions = {node.successful_transmission} | frame dropped = {node.frame_dropped}")


