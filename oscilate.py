from quanser.hardware import HIL, HILError, Clock
import numpy as np
import time
control_motor_channels = np.array([0], dtype=np.uint32)  # Analog output channel 0: Motor control voltage
activate_motor_channels = np.array([0], dtype=np.uint32)  # Digital output channel 0: Motor amplifier enable

# Encoder Channel 0: Motor shaft encoder (counts)
# Encoder Channel 1: Pendulum encoder (counts) - if pendulum module attached
encoder_channels = np.array([0], dtype=np.uint32)  # Just motor encoder for now

# Control parameters
FREQUENCY = 10  # Hz - control loop frequency
DURATION = 10    # seconds
PERIOD = 0.5     # Oscillation period in seconds


def oscilate_with_task(card:HIL):
    """Use HIL tasks for precise real-time control timing."""
    
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
    
    write_task = card.task_create_analog_writer(
        samples_in_buffer,          # buffer size
        control_motor_channels,     # analog channels to write
        len(control_motor_channels)
    )
    
    print(f"Tasks created (buffer={samples_in_buffer})")
    print(f"Running for {DURATION} seconds at {FREQUENCY} Hz...")
    
    total_samples = FREQUENCY * DURATION
    oscillation_samples = int(FREQUENCY * PERIOD / 2)  # samples per half-period
    
    try:
        # Start both tasks
        card.task_start(read_task, Clock.HARDWARE_CLOCK_0, FREQUENCY, total_samples)
        card.task_start(write_task, Clock.HARDWARE_CLOCK_0, FREQUENCY, total_samples)
        print("Tasks started")
        
        samples_processed = 0
        
        while samples_processed < total_samples:
            # Determine voltage based on oscillation
            cycle_position = samples_processed % (oscillation_samples * 2)
            if cycle_position < oscillation_samples:
                voltage[0] = 1.0   # +1V for first half
            else:
                voltage[0] = -1.0  # -1V for second half
            
            # Write voltage
            card.task_write_analog(write_task, 1, voltage)
            
            # Read encoder
            card.task_read_encoder(read_task, 1, encoder_counts)
            
            samples_processed += 1
            
            # Print every second
            if samples_processed % FREQUENCY == 0:
                print(f"   t={samples_processed/FREQUENCY:.1f}s, Encoder: {encoder_counts[0]:+6d} counts, V={voltage[0]:+.1f}")
        
        print("Oscillation completed successfully")
        
    except HILError as e:
        print(f"HIL Error during task: {e}")
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        # Stop and delete tasks
        try:
            card.task_stop(read_task)
            card.task_stop(write_task)
            card.task_delete(read_task)
            card.task_delete(write_task)
            print("Tasks stopped and deleted")
        except:
            pass
        
        # Stop the motor
        card.write_analog(control_motor_channels, 1, np.array([0.0], dtype=np.float64))
        print("Motor stopped")


if __name__ == "__main__":
    card = None
    try:
        card = HIL()
        card.open("qube_servo3_usb", "0")
        print("Card opened")
        
        # Enable amplifier
        card.write_digital(activate_motor_channels, 1, np.array([1], dtype=np.int8))
        print("Amplifier enabled")
        time.sleep(0.5)
        
        oscilate_with_task(card)
        
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
    
