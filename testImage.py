# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 17:54:52 2024

@author: Daniel
"""
import cv2
import threading
import time
from ultralytics import YOLO

model = YOLO('yolov8n.pt')

results = model("C:/Users/Daniel/Downloads/Imagen de WhatsApp 2024-06-05 a las 21.33.06_513aef84.jpg")[0]
frame = cv2.imread("C:/Users/Daniel/Downloads/Imagen de WhatsApp 2024-06-05 a las 21.33.06_513aef84.jpg")
box_list=[]
class_list = []
for result in results:
    boxes = result.boxes.xyxy.numpy()
    scores = result.boxes.conf.numpy()  # Confianza de la detección
    class_ids = result.boxes.cls.numpy()
    for box, score, class_id in zip(boxes, scores, class_ids):
        box_list.append(box.tolist())
        class_list.append(str(class_id))
        xmin, ymin, xmax, ymax = map(int, box)
        color = (0, 255, 0)  # Color del cuadro

        # Dibujar el cuadro delimitador
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
        # Dibujar la etiqueta
        cv2.putText(frame, 'person', (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.imshow("test",frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
             break



#annotated_frame = results.plot()
#cv2.imshow("test",annotated_frame)

from datetime import datetime
import pytz
timezone = pytz.timezone('America/Bogota')
# Obtener la hora actual en esa zona horaria
now = datetime.now(timezone)
# Formatear el timestamp
timestamp_aa = now.strftime('%Y-%m-%d/%H:%M:%S')

print(class_list)
# message = {
#     'timestamp': timestamp,
#     'person_count': person_count,
#     'detected_people': detected_people
# }