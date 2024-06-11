'''
Developed by Balum S.A. under supervision of Daniel Zambrano Acosta. 
This code is used to connect to the CCTV, which is paired with AWS through a site-to-site VPN.
'''

import cv2
import json
import time
import pytz
import boto3
import random
import string
import threading
from datetime import datetime
from ultralytics import YOLO




class ReadingCamera:
    
    def __init__(self,rtsp):
        self.rtsp = rtsp
        self.threads = []
    
    @staticmethod
    def random_string(N=20):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
    @staticmethod
    def get_timestamp(timezone_str='America/Bogota'):
        timezone = pytz.timezone(timezone_str)
        now = datetime.now(timezone)
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        return timestamp


    def readVideo(self,rtsp):
        box_etector = YOLO('yolov8n.pt')
        sqs_client = boto3.client('sqs')

        frameCount = 0
        try:
            video_capture = cv2.VideoCapture(rtsp)
            if not video_capture.isOpened():
                raise Exception(f"fail connection to camera in {rtsp}")

            while video_capture.isOpened():
                ret, frame = video_capture.read()
                if not ret:
                    print("Error al leer el frame del stream de la cámara")
                    time.sleep(1)
                    video_capture.release()
                    video_capture = cv2.VideoCapture(rtsp)
                    break
                
                frameCount += 1

                if frameCount == 29:
                    nameIdList = []
                    boxList  = []
                    scoreList = []
                    #Display video
                    #cv2.imshow(f"Camera{rtsp}",frame)
                    results = box_etector(frame, verbose = False)[0]
                    
                    for result in results:
                        class_ids = result.boxes.cls.numpy()
                        boxes = result.boxes.xyxy.numpy()
                        scores = result.boxes.conf.numpy()  # Confianza de la detección
                        
                        for classId, box, score  in zip(class_ids, boxes, scores):
                            if classId == 0.0:
                                nameIdList.append(classId)
                                boxList.append(box.tolist())
                                scoreList.append(scores.tolist())
                                
                            print(f'{classId},{score}')
                    if len(boxList) > 0: 
                        timestamp = self.get_timestamp()
                        response = sqs_client.send_message(
                            QueueUrl='https://sqs.us-east-1.amazonaws.com/939586641042/demoIntergraficas.fifo',
                            MessageBody=json.dumps({'Name_ID': str(nameIdList), 
                                                    'Box':str(boxList),
                                                    'Score': str(scoreList),
                                                    'Time_Stamp': timestamp}),
                            MessageGroupId="camera_27", 
                            MessageDeduplicationId=self.random_string())
                        print(response)
                        
                    

                            #annotated_frame = results.plot()
                            #cv2.imshow(f"Camera{rtsp}",annotated_frame)
                            # if cv2.waitKey(1) & 0xFF == ord('q'):
                            #     break
                        
                    frameCount = 0
                    
                    #print(f"Camera {rtsp}: Result of prediction {result}")
                    # if cv2.waitKey(1) & 0xFF == ord('q'):
                    #     break
                    #time.sleep(0.1)
        
            video_capture.release()
           #cv2.destroyAllWindows()


        except Exception as e:
            print(f"Error at camera {rtsp}: {e}")

    def startReading (self):
        for url in self.rtsp:
            thread = threading.Thread(target=self.readVideo, args=(url,))
            self.threads.append(thread)
            thread.start()

        for thread in self.threads:
            thread.join()