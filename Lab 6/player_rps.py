import time
import board
import busio
import adafruit_mpr121
import paho.mqtt.client as mqtt

# Optional: Display support
try:
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_rgb_display.st7789 as st7789
    DISPLAY_AVAILABLE = True
except ImportError:
    DISPLAY_AVAILABLE = False
    print("Display libraries not available - running in headless mode")

PLAYER_ID = "player1"

# Display setup
disp = None
canvas = None
draw = None
font_large = None
font_medium = None
font_small = None

def display_message(text, color=(255, 255, 255), bg_color=(0, 0, 0), subtext=None):
    """Display a message on the screen"""
    if not DISPLAY_AVAILABLE or disp is None:
        return
    
    try:
        # Clear screen
        draw.rectangle((0, 0, 240, 135), fill=bg_color)
        
        # Split text into lines if needed
        lines = text.split('\n')
        y_offset = 20
        
        # Draw main text
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_large)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (240 - text_width) // 2
            draw.text((x, y_offset), line, font=font_large, fill=color)
            y_offset += text_height + 5
        
        # Draw subtext if provided
        if subtext:
            bbox = draw.textbbox((0, 0), subtext, font=font_small)
            text_width = bbox[2] - bbox[0]
            x = (240 - text_width) // 2
            draw.text((x, 110), subtext, font=font_small, fill=color)
        
        disp.image(canvas)
    except Exception as e:
        print(f"Display error: {e}")

def setup_display():
    """Setup the MiniPiTFT display if available"""
    global disp, canvas, draw, font_large, font_medium, font_small
    
    if not DISPLAY_AVAILABLE:
        return False
    
    try:
        # Configuration for CS and DC pins
        cs_pin = digitalio.DigitalInOut(board.D5)
        dc_pin = digitalio.DigitalInOut(board.D25)
        reset_pin = None
        BAUDRATE = 64000000
        
        # Backlight
        backlight = digitalio.DigitalInOut(board.D22)
        backlight.switch_to_output()
        backlight.value = True
        
        # Setup SPI bus
        spi = board.SPI()
        
        # Create the ST7789 display
        disp = st7789.ST7789(
            spi,
            cs=cs_pin,
            dc=dc_pin,
            rst=reset_pin,
            baudrate=BAUDRATE,
            width=135,
            height=240,
            x_offset=53,
            y_offset=40,
            rotation=90
        )
        
        # After rotation, width and height are swapped
        WIDTH = 240
        HEIGHT = 135
        
        canvas = Image.new("RGB", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(canvas)
        
        # Load fonts
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Show initial message
        display_message("Waiting for\ngame to start...", (255, 255, 255))
        return True
    except Exception as e:
        print(f"Display setup failed: {e}")
        return False

# Setup display
display_ready = setup_display()

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Player {PLAYER_ID} connected!")
    client.subscribe("game/winner")
    client.subscribe("game/start_round")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    
    if topic == "game/winner":
        if payload == "tie":
            print(f"\n{'='*50}")
            print("RESULT: It's a TIE!")
            print(f"{'='*50}\n")
            display_message("TIE!", (255, 255, 0), (0, 0, 0), "Try again!")
        elif payload == PLAYER_ID:
            print(f"\n{'='*50}")
            print(f"*** YOU WIN! ***")
            print(f"{'='*50}\n")
            display_message("YOU WIN!", (0, 255, 0), (0, 0, 0), "Congratulations!")
        else:
            print(f"\n{'='*50}")
            print(f"You LOST. {payload} won.")
            print(f"{'='*50}\n")
            display_message("YOU LOST", (255, 0, 0), (0, 0, 0), f"{payload} won")
    elif topic == "game/start_round":
        print(f"\n>>> New round starting! Choose your move...")
        display_message("New Round!", (255, 255, 255), (0, 0, 0), "Choose your move")

# MQTT setup
client = mqtt.Client()
client.username_pw_set("idd", "device@theFarm")
client.on_connect = on_connect
client.on_message = on_message
client.connect("farlab.infosci.cornell.edu", 1883, 60)
client.loop_start()

# MPR121 setup
i2c = busio.I2C(board.SCL, board.SDA)
mpr121 = adafruit_mpr121.MPR121(i2c)

# Electrode -> move mapping
mapping = {
    0: "rock",
    1: "paper",
    2: "scissors"
}

def publish_move(move):
    topic = f"game/player/{PLAYER_ID}/move"
    print(f"[SEND] {move}")
    client.publish(topic, move)
    # Show move on display
    display_message(f"You chose:\n{move.upper()}", (255, 255, 255), (0, 0, 0), "Waiting for result...")

print(f"Player {PLAYER_ID} ready!")
print("Touch an electrode to play:")
print("  - Electrode 0: Rock")
print("  - Electrode 1: Paper")
print("  - Electrode 2: Scissors")
print("Waiting for game to start...\n")

last_state = [False] * 12

while True:
    for i in range(12):
        touched = mpr121[i].value
        if touched and not last_state[i]:  # new touch
            if i in mapping:
                publish_move(mapping[i])
        last_state[i] = touched

    time.sleep(0.05)
