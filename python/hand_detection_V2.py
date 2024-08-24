import cv2
import math
import asyncio
import websockets
import json
from cvzone.HandTrackingModule import HandDetector

# Initialize the camera and hand detector
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Customizable parameters
TOUCH_THRESHOLD = 30
ZOOM_NORMALIZATION = 200
DISPLAY_DEBUG = True

def calculate_angle(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang + 360 if ang < 0 else ang

def fingers_touching(finger1, finger2, lm_list, threshold=TOUCH_THRESHOLD):
    distance, _, _ = detector.findDistance(lm_list[finger1][:2], lm_list[finger2][:2], None)
    return distance < threshold

def process_hand(hand, img_shape):
    lm_list = hand['lmList']
    
    rel_x = lm_list[8][0] / img_shape[1]
    rel_y = 1 - (lm_list[8][1] / img_shape[0])  # Invert Y-axis
    
    z_length, _, _ = detector.findDistance(lm_list[8][:2], lm_list[4][:2], None)
    zoom_level = z_length / ZOOM_NORMALIZATION
    
    angle = calculate_angle(lm_list[0][:2], lm_list[5][:2], lm_list[17][:2])
    
    finger_states = {
        'thumb_up': lm_list[4][1] < lm_list[3][1],
        'index_up': lm_list[8][1] < lm_list[6][1],
        'middle_up': lm_list[12][1] < lm_list[10][1],
        'ring_up': lm_list[16][1] < lm_list[14][1],
        'pinky_up': lm_list[20][1] < lm_list[18][1],
    }
    
    touches = {
        'pointer_thumb': fingers_touching(4, 8, lm_list),
        'pointer_middle': fingers_touching(8, 12, lm_list),
        'pinky_thumb': fingers_touching(4, 20, lm_list),
        'thumb_middle': fingers_touching(4, 12, lm_list),
    }
    
    return {
        'x': rel_x,
        'y': rel_y,
        'zoom': zoom_level,
        'angle': angle,
        'finger_states': finger_states,
        'touches': touches,
    }

async def hand_tracking(websocket, path):
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        hands, img = detector.findHands(frame)

        hand_data = {'left': None, 'right': None}
        
        for hand in hands:
            hand_type = 'left' if hand['type'] == 'Left' else 'right'
            hand_data[hand_type] = process_hand(hand, img.shape)
        
        if DISPLAY_DEBUG:
            display_debug_info(img, hand_data)

        await websocket.send(json.dumps(hand_data))

        cv2.imshow('Hand Tracking', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def display_debug_info(img, hand_data):
    for hand_type in ['left', 'right']:
        if hand_data[hand_type]:
            y_offset = 30 if hand_type == 'left' else img.shape[0] - 180
            x_offset = 10 if hand_type == 'left' else img.shape[1] - 200
            color = (255, 0, 0) if hand_type == 'left' else (0, 255, 0)
            
            cv2.putText(img, f"{hand_type.capitalize()} Hand", (x_offset, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            y_offset += 30
            for key, value in hand_data[hand_type]['finger_states'].items():
                cv2.putText(img, f"{key}: {value}", (x_offset, y_offset), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                y_offset += 20
            for key, value in hand_data[hand_type]['touches'].items():
                cv2.putText(img, f"{key}: {value}", (x_offset, y_offset), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                y_offset += 20

async def main():
    server = await websockets.serve(hand_tracking, "localhost", 6789)
    print("WebSocket server started on ws://localhost:6789")
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()