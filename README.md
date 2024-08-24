# Digital_biology_selfplay

To run the application:

1) download codebase
2) create a virtual environment in the root of the downloaded codebase
3) activate virtual environment
4) pip install -r requirements.txt
5) open 4 terminal windows
6) on each window, cd into the root of the downloaded codebase
7) in the first window:
     cd into the "python" directory
   then run:
     python -m http.server 8000 // this is for the web server for the index.html 
9) in the second window run:
     cd into the "python" directory
   then run:
     python server.py
10) in the second window run:
     cd into the "python" directory
   then run:
     python hand_detection_V2.py
12) in the second window run:
     cd into the "python" directory
   then run:
     python voice_recognition.py
