import sys
import time

def test_quanser_api():
    """
    Attempts to import the Quanser API, open a connection to the Qube,
    read its basic state, and then safely close the connection.
    """
    print("=" * 50)
    print("Qube Servo 2 - API Installation Test")
    print("=" * 50)

    # Step 1: Test API Import
    print("\n1. Testing Quanser API import...")
    try:
        # Import the main HIL (Hardware-In-the-Loop) class
        from quanser.hardware import HIL, HILError, Clock
        print("   ✅ SUCCESS: 'HIL', 'HILError', and 'Clock' imported.")
    except ImportError as e:
        print(f"   ❌ FAILED: Could not import Quanser modules. Error: {e}")
        print("   Please ensure the Quanser Python API is installed and your PYTHONPATH is set correctly.")
        return False

    # Step 2: Create a HIL card object and attempt to open the default device
    card = None
    print("\n2. Attempting to open connection to Qube...")
    
    # Try different board identifiers - adjust based on your hardware
    board_types = [
        "qube_servo2_usb",   # Qube Servo 2
    ]
    
    try:
        card = HIL()
        opened = False
        for board_type in board_types:
            try:
                print(f"   Trying board type: '{board_type}'...")
                card.open(board_type, "0")
                print(f"   ✅ SUCCESS: HIL card opened with '{board_type}'.")
                opened = True
                break
            except HILError as e:
                print(f"   ⚠️  '{board_type}' failed: {e}")
                continue
        
        if not opened:
            print("   ❌ FAILED: Could not open any board type.")
            print("   Please check your hardware and QUARC installation.")
            return False
    except:
        print("   ❌ FAILED: Unexpected error during HIL card creation/opening.")
        return False
    
    import numpy as np
    
    # Step 3: Enable the motor amplifier (turns LED green)
    print("\n3. Enabling motor amplifier...")
    try:
        # Digital output channel 0 controls the amplifier enable
        # Setting it to 1 (True) enables the amplifier
        digital_channels = np.array([0], dtype=np.uint32)
        enable_values = np.array([1], dtype=np.int8)
        
        card.write_digital(digital_channels, len(digital_channels), enable_values)
        print("   ✅ SUCCESS: Amplifier enabled (LED should turn green).")
        time.sleep(0.5)  # Give it time to enable
    except HILError as e:
        print(f"   ⚠️  WARNING: Could not enable amplifier. HILError: {e}")
    
    # Step 4: Test reading encoder inputs (motor and pendulum position)
    print("\n4. Testing encoder read...")
    try:
        # For Qube Servo 2/3:
        # Encoder Channel 0: Motor shaft encoder (counts)
        # Encoder Channel 1: Pendulum encoder (counts) - if pendulum module attached
        encoder_channels = np.array([0], dtype=np.uint32)
        num_encoder_channels = len(encoder_channels)
        encoder_counts = np.zeros(num_encoder_channels, dtype=np.int32)

        # Perform a single encoder read
        card.read_encoder(encoder_channels, num_encoder_channels, encoder_counts)
        print(f"   ✅ SUCCESS: Encoder data read.")
        print(f"      Motor Encoder (Ch0): {encoder_counts[0]} counts")
    except HILError as e:
        print(f"   ⚠️  WARNING: Could not read encoders. HILError: {e}")

    # Step 5: Test motor movement
    print("\n5. Testing motor movement...")
    try:
        pwm_channels = np.array([0], dtype=np.uint32)
        
        # Apply a small voltage to move the motor
        print("   Applying +0.1V for 0.5 seconds...")
        pwm_values = np.array([0.5], dtype=np.float64)
        card.write_analog(pwm_channels, len(pwm_channels), pwm_values)
        time.sleep(0.5)
        
        # Read encoder to see movement
        card.read_encoder(encoder_channels, num_encoder_channels, encoder_counts)
        print(f"      Encoder after +1V: {encoder_counts[0]} counts")
        
        # Stop the motor
        print("   Stopping motor (0V)...")
        pwm_values = np.array([0.0], dtype=np.float64)
        card.write_analog(pwm_channels, len(pwm_channels), pwm_values)
        
        print(f"   ✅ SUCCESS: Motor test complete.")
    except HILError as e:
        print(f"   ⚠️  WARNING: Could not control motor. HILError: {e}")

    # Step 6: Disable amplifier and close connection
    print("\n6. Disabling amplifier and closing connection...")
    try:
        # Disable the amplifier before closing
        disable_values = np.array([0], dtype=np.int8)
        card.write_digital(digital_channels, len(digital_channels), disable_values)
        print("   ✅ Amplifier disabled (LED should turn red).")
    except HILError as e:
        print(f"   ⚠️  WARNING: Could not disable amplifier. HILError: {e}")
    
    try:
        if card is not None:
            card.close()
            print("   ✅ SUCCESS: HIL card closed cleanly.")
    except HILError as e:
        print(f"   ⚠️  WARNING: Error during close. HILError: {e}")
        return False

    print("\n" + "=" * 50)
    print("BASIC CONNECTION TEST COMPLETE.")
    print("Check above for any ❌ FAILED or ⚠️  WARNING messages.")
    print("=" * 50)
    return True
def setup_api():
    """
    Setup function to initialize the Quanser API.
    This can be expanded to include any setup routines needed.
    """
    """
    Attempts to import the Quanser API, open a connection to the Qube,
    read its basic state, and then safely close the connection.
    """
    print("=" * 50)
    print("Qube Servo 2 - API Installation Test")
    print("=" * 50)

    # Step 1: Test API Import
    print("\n1. Testing Quanser API import...")
    try:
        # Import the main HIL (Hardware-In-the-Loop) class
        from quanser.hardware import HIL, HILError, Clock
        print("   ✅ SUCCESS: 'HIL', 'HILError', and 'Clock' imported.")
    except ImportError as e:
        print(f"   ❌ FAILED: Could not import Quanser modules. Error: {e}")
        print("   Please ensure the Quanser Python API is installed and your PYTHONPATH is set correctly.")
        return False

    # Step 2: Create a HIL card object and attempt to open the default device
    card = None
    print("\n2. Attempting to open connection to Qube...")
    
    board_types = [
        "qube_servo2_usb",   # Qube Servo 2
    ]
    
    try:
        card = HIL()
        opened = False
        for board_type in board_types:
            try:
                print(f"   Trying board type: '{board_type}'...")
                card.open(board_type, "0")
                print(f"   ✅ SUCCESS: HIL card opened with '{board_type}'.")
                opened = True
                break
            except HILError as e:
                print(f"   ⚠️  '{board_type}' failed: {e}")
                continue
        
        if not opened:
            print("   ❌ FAILED: Could not open any board type.")
            print("   Please check your hardware and QUARC installation.")
            return False
    except:
        print("   ❌ FAILED: Unexpected error during HIL card creation/opening.")
        return False
    
    import numpy as np
    
    # Step 3: Enable the motor amplifier (turns LED green)
    print("\n3. Enabling motor amplifier...")
    try:
        # Digital output channel 0 controls the amplifier enable
        # Setting it to 1 (True) enables the amplifier
        digital_channels = np.array([0], dtype=np.uint32)
        enable_values = np.array([1], dtype=np.int8)
        
        card.write_digital(digital_channels, len(digital_channels), enable_values)
        print("   ✅ SUCCESS: Amplifier enabled (LED should turn green).")
        time.sleep(0.5)  # Give it time to enable
    except HILError as e:
        print(f"   ⚠️  WARNING: Could not enable amplifier. HILError: {e}")
    
    # Step 4: Test reading encoder inputs (motor and pendulum position)
    print("\n4. Testing encoder read...")
    try:
        # For Qube Servo 2/3:
        # Encoder Channel 0: Motor shaft encoder (counts)
        # Encoder Channel 1: Pendulum encoder (counts) - if pendulum module attached
        encoder_channels = np.array([0], dtype=np.uint32)
        num_encoder_channels = len(encoder_channels)
        encoder_counts = np.zeros(num_encoder_channels, dtype=np.int32)

        # Perform a single encoder read
        card.read_encoder(encoder_channels, num_encoder_channels, encoder_counts)
        print(f"   ✅ SUCCESS: Encoder data read.")
        print(f"      Motor Encoder (Ch0): {encoder_counts[0]} counts")
    except HILError as e:
        print(f"   ⚠️  WARNING: Could not read encoders. HILError: {e}")

    # Step 5: Test motor movement
    print("\n5. Testing motor movement...")
    try:
        pwm_channels = np.array([0], dtype=np.uint32)
        
        # Apply a small voltage to move the motor
        print("   Applying +0.1V for 0.5 seconds...")
        pwm_values = np.array([0.5], dtype=np.float64)
        card.write_analog(pwm_channels, len(pwm_channels), pwm_values)
        time.sleep(0.5)
        
        # Read encoder to see movement
        card.read_encoder(encoder_channels, num_encoder_channels, encoder_counts)
        print(f"      Encoder after +1V: {encoder_counts[0]} counts")
        
        # Stop the motor
        print("   Stopping motor (0V)...")
        pwm_values = np.array([0.0], dtype=np.float64)
        card.write_analog(pwm_channels, len(pwm_channels), pwm_values)
        
        print(f"   ✅ SUCCESS: Motor test complete.")
    except HILError as e:
        print(f"   ⚠️  WARNING: Could not control motor. HILError: {e}")

    # Step 6: Disable amplifier and close connection
    print("\n6. Disabling amplifier and closing connection...")
    try:
        # Disable the amplifier before closing
        disable_values = np.array([0], dtype=np.int8)
        card.write_digital(digital_channels, len(digital_channels), disable_values)
        print("   ✅ Amplifier disabled (LED should turn red).")
    except HILError as e:
        print(f"   ⚠️  WARNING: Could not disable amplifier. HILError: {e}")
    
    try:
        if card is not None:
            card.close()
            print("   ✅ SUCCESS: HIL card closed cleanly.")
    except HILError as e:
        print(f"   ⚠️  WARNING: Error during close. HILError: {e}")
        return False

    return True
def close_api():
    """
    Cleanup function to close the Quanser API.
    This can be expanded to include any cleanup routines needed.
    """
    pass  # Currently no cleanup actions required
def get_state():
    """
    Function to retrieve the current state from the Quanser hardware.
    This is a placeholder and should be implemented as needed.
    """
    pass  # Implementation depends on specific requirements
def set_action(action):
    """
    Function to set an action on the Quanser hardware.
    This is a placeholder and should be implemented as needed.
    """
    pass  # Implementation depends on specific requirements
if __name__ == "__main__":
    # Run the test function
    success = test_quanser_api()
    # Exit with a code indicating success (0) or failure (1)
    sys.exit(0 if success else 1)