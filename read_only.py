# Gabriel Vallat 17.02.2026
# Small script to read the values of the encoders and test the connection

from quanser.hardware import HIL, HILError, Clock
import numpy as np
import time

# Control channels
control_motor_channels = np.array([0], dtype=np.uint32)  # Analog output channel 0: Motor control voltage
activate_motor_channels = np.array([0], dtype=np.uint32)  # Digital output channel 0: Motor amplifier enable

# Encoder Channel 0: Motor shaft encoder (counts)
# Encoder Channel 1: Pendulum encoder (counts) - if pendulum module attached
encoder_channels = np.array([0,1], dtype=np.uint32)  # Just motor encoder for now

# Control parameters
FREQUENCY = 500  # Hz - control loop frequency
DURATION = 30    # seconds

def read_encoders(card:HIL):
    """Use HIL tasks for precise real-time control timing."""
    
    encoder_counts = np.zeros(len(encoder_channels), dtype=np.int32)
    # Create separate tasks for reading
    # Buffer size for samples
    samples_in_buffer = FREQUENCY  # 1 second worth of samples
    
    read_task = card.task_create_encoder_reader(
        samples_in_buffer,   # buffer size
        encoder_channels,    # encoder channels to read
        len(encoder_channels)
    )
    
    print(f"Tasks created (buffer={samples_in_buffer})")
    print(f"Running for {DURATION} seconds at {FREQUENCY} Hz...")
    
    total_samples = FREQUENCY * DURATION    
    try:
        card.task_start(read_task, Clock.HARDWARE_CLOCK_0, FREQUENCY, total_samples)
        print("Tasks started")
        
        samples_processed = 0
        prev_encoder_counts = np.zeros(len(encoder_channels), dtype=np.int32)
        card.task_read_encoder(read_task, 1, prev_encoder_counts)
        while samples_processed < total_samples:
            card.task_read_encoder(read_task, 1, encoder_counts)
            print(f"Encoder counts: {encoder_counts}")
            v = encoder_counts - prev_encoder_counts
            prev_encoder_counts = encoder_counts.copy()

            
            # Print every second
            if samples_processed % FREQUENCY == 0:
                print(f"   t={samples_processed/FREQUENCY:.1f}s, Encoder: {encoder_counts[1]:+6d} counts")
            samples_processed += 1
        print("Loop completed successfully")
        
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
# if __name__ == "__main__": should always be at the beginning of the script,
# This allows the script not to be called when imported as a module, and only run when executed directly.
if __name__ == "__main__":
    card = None
    #Using try and except allows us to always disable the amplifier and close the card connection cleanly, even if an error occurs during the test
    try:
        card = HIL()
        card.open("qube_servo2_usb", "0")
        print("Card opened")
        
        read_encoders(card)
        
    except HILError as e:
        print(f"HIL Error: {e}")
    finally:
        if card is not None:
            try:
                # Disable amplifier (should not be on, this is a safety measure)
                card.write_digital(activate_motor_channels, 1, np.array([0], dtype=np.int8))
                print("Amplifier disabled")
            except:
                pass
            card.close()
            print("Card closed")
    
