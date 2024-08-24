# python/voice_recognition.py

import speech_recognition as sr
import asyncio
import websockets
import json

async def recognize_voice(websocket, path):
    recognizer = sr.Recognizer()
    
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source, timeout=5)
                try:
                    text = recognizer.recognize_google(audio)
                    print(f"Voice Recognition Result: {text}")
                    
                    # Send the recognized text via WebSocket
                    await websocket.send(json.dumps({"voice_command": text}))
                    
                except sr.UnknownValueError:
                    print("Voice Recognition Error: Could not understand audio")
                except sr.RequestError:
                    print("Voice Recognition Error: API unavailable")
        except Exception as e:
            print(f"Error in voice recognition: {str(e)}")

async def main():
    server = await websockets.serve(recognize_voice, "localhost", 6790)
    print("Voice recognition WebSocket server started on ws://localhost:6790")
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Voice recognition server stopped by user")
