from quanser.hardware import HIL, HILError, Clock
import numpy as np
import time
import torch
from torch import nn
control_motor_channels = np.array([0], dtype=np.uint32)  # Analog output channel 0: Motor control voltage
activate_motor_channels = np.array([0], dtype=np.uint32)  # Digital output channel 0: Motor amplifier enable

# Encoder Channel 0: Motor shaft encoder (counts)
# Encoder Channel 1: Pendulum encoder (counts) - if pendulum module attached
# Encoder Channel 2
encoder_channels = np.array([0], dtype=np.uint32)  # Just motor encoder for now

# Control parameters
FREQUENCY = 500  # Hz - control loop frequency
DURATION = 10    # seconds
PERIOD = 0.5     # Oscillation period in seconds


def rollout(card:HIL,network:nn.Module,n_prev_states:int=5):
    """Use HIL tasks for precise real-time control timing."""
    state = np.zeros((len(encoder_channels)*n_prev_states), dtype=np.float32)
    encoder_counts = np.zeros(len(encoder_channels), dtype=np.int32)
    voltage = np.array([0.0], dtype=np.float64)
    
    # Create separate tasks for reading and writing
    # Buffer size for samples
    samples_in_buffer = FREQUENCY  # 1 second worth of samples
    
    read_task = card.task_create_encoder_reader(
        samples_in_buffer,   # buffer size
        encoder_channels,    # encoder channels to read
        len(encoder_channels)
    )
    #write_task = card.task_create_analog_writer(
    #    samples_in_buffer,          # buffer size
    #    control_motor_channels,     # analog channels to write
    #    len(control_motor_channels)
    #)
    
    print(f"Tasks created (buffer={samples_in_buffer})")
    print(f"Running for {DURATION} seconds at {FREQUENCY} Hz...")
    
    total_samples = FREQUENCY * DURATION    
    
    try:
        # Start both tasks
        card.task_start(read_task, Clock.HARDWARE_CLOCK_0, FREQUENCY, total_samples)
        #card.task_start(write_task, Clock.HARDWARE_CLOCK_1, FREQUENCY, total_samples)
        print("Tasks started")
        
        samples_processed = 0
        
        card.task_read_encoder(read_task, n_prev_states, state)
        states = []
        actions = []
        rewards = []
        while samples_processed < total_samples:
            #print("Reading encoder")
            # Read encoder
            card.task_read_encoder(read_task, 1, encoder_counts)
            #print(f"Encoder counts: {encoder_counts}")
            state = np.roll(state, -len(encoder_channels))
            state[-len(encoder_channels):] = encoder_counts
            states.append(state.copy())
            nn_input = torch.tensor(encoder_counts/500,dtype=torch.float32)
            action = network(nn_input)
            voltage = 10*action.detach().numpy()
            # Write voltage
            #print("Writing control")
            actions.append(action.detach())
            card.write_analog(control_motor_channels, 1, voltage)
            rewards.append(compute_reward(state,voltage))
            samples_processed += 1
            
            # Print every second
            if samples_processed % FREQUENCY == 0:
                print(f"   t={samples_processed/FREQUENCY:.1f}s, Encoder: {encoder_counts[0]:+6d} counts, a={voltage[0]:+.1f}")
        
        print("Rollout completed successfully")
        
    except HILError as e:
        print(f"HIL Error during task: {e}: {HILError.get_error_message(e)}")
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        # Stop and delete tasks
        try:
            card.task_stop(read_task)
            card.task_delete(read_task)
            print("Tasks stopped and deleted")
        except:
            pass
        
        # Stop the motor
        card.write_analog(control_motor_channels, 1, np.array([0.0], dtype=np.float64))
        print("Motor stopped")
def compute_reward(state:np.ndarray,action:np.ndarray):
    # Reward is negative absolute pendulum angle minus small action penalty
    pendulum_angle = state[-1]  # Assuming encoder channel 1 is pendulum
    reward = -abs(pendulum_angle)/1000.0 - 0.01*(action[0]**2)
    return reward
def train(card:HIL,network:nn.Module,n_episodes:int):
    for episode in range(n_episodes):
        print(f"Starting episode {episode+1}/{n_episodes}")
        buffer = rollout(card,network)
        print(f"Episode {episode+1} completed\n")
        update_pol(network,buffer)
def update_pol(network:nn.Module,buffer):
    pass
if __name__ == "__main__":
    card = None
    network = nn.Sequential(nn.Linear(len(encoder_channels), 16),nn.ReLU(),
                            nn.Linear(16, 16),nn.ReLU(),
                            nn.Linear(16, 1),nn.Tanh())
    try:
        card = HIL()
        card.open("qube_servo3_usb", "0")
        print("Card opened")
        
        # Enable amplifier
        card.write_digital(activate_motor_channels, 1, np.array([1], dtype=np.int8))
        print("Amplifier enabled")
        time.sleep(0.5)
        
        train(card,network,10)
        
    except HILError as e:
        print(f"HIL Error: {e}")
    finally:
        if card is not None:
            try:
                # Disable amplifier
                card.write_digital(activate_motor_channels, 1, np.array([0], dtype=np.int8))
                print("Amplifier disabled")
            except:
                pass
            card.close()
            print("Card closed")
    
