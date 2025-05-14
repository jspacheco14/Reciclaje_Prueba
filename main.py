# Libraries
from tkinter import *
from PIL import Image, ImageTk
import imutils
import cv2
import numpy as np
from ultralytics import YOLO
import math
import requests
from datetime import datetime
from config import Point, get_categories_information, Timer, BASE_API_URL



class CategoryInference:

    def __init__(self,seconds_to_log=10):
        # Ventana principal
        self.seconds_to_log = seconds_to_log #10 segundos para loguear
        self.pantalla = Tk()
        self.pantalla.title("RECICLAJE INTELIGENTE")
        self.pantalla.geometry("1280x720")

        # Background
        imagenF = PhotoImage(file="setUp/Canva.png")
        self.background = Label(image=imagenF, text="Inicio")
        self.background.place(x=0, y=0, relwidth=1, relheight=1)

        # Model
        self.model = YOLO('Modelo/best.pt')

        # Video
        self.lblVideo = Label(self.pantalla)
        self.lblVideo.place(x=320, y=180)

        # Category Image
        self.lblimg = Label(
            self.pantalla
        )
        self.lblimg.place(x=75, y=260)

        # Category txt

        self.lblimgtxt = Label(
            self.pantalla
        )
        self.lblimgtxt.place(x=995, y=310)

        # Elegimos la camara
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

        self.first_execution = True
        self.log_timer = Timer()

        self.category_info = get_categories_information()

        self.__scanning()
        self.pantalla.mainloop()
        

    def __clean_lbl(self, ):
        # Clean
        self.lblimg.config(image='')
        self.lblimgtxt.config(image='')

    def __draw_category_info(self, img, imgtxt):

        img_ = ImageTk.PhotoImage(image=img)
        self.lblimg.configure(image=img_)
        self.lblimg.image = img_

        img_txt = ImageTk.PhotoImage(image=imgtxt)
        self.lblimgtxt.configure(image=img_txt)
        self.lblimgtxt.image = img_txt


    def __draw_category_rect(self, frame, category_name: str, probability: float, fp: Point, sp: Point, color: tuple[int]):
        # Draw
        cv2.rectangle(frame, fp.get_tuple(), sp.get_tuple(), color, 2)
        # Text

        text = f'{category_name} {int(probability) * 100}%'
        sizetext = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        dim = sizetext[0]
        baseline = sizetext[1]
        # Rect
        cv2.rectangle(frame, (fp.x, fp.y - dim[1] - baseline), (fp.x + dim[0], fp.y + baseline), (0, 0, 0),cv2.FILLED)
        cv2.putText(frame, text, (fp.x, fp.y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)


    # __scanning Function
    def __scanning(self):
        # Interfaz
        detect = False

        # Read VideoCapture
        if self.cap is not None:
            ret, frame = self.cap.read()
            # True
            if ret == True:
                frame_show =cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Yolo | AntiSpoof
                results = self.model(frame, stream=True, verbose=False)
                for res in results:
                    # Box
                    boxes = res.boxes
                    for box in boxes:
                        detect = True
                        # Bounding box

                        p1 = Point()
                        p2 = Point()

                        p1.x, p1.y, p2.x, p2.y = box.xyxy[0]


                        # Class
                        cls = int(box.cls[0])

                        # Confidence
                        conf = math.ceil(box.conf[0])
                        #print(f"Clase: {cls} Confidence: {conf}")
                        self.__draw_category_rect(frame_show, self.category_info[cls].name, conf,p1,p2, self.category_info[cls].color)
                        # Clasificacion
                        self.__draw_category_info(self.category_info[cls].visual_image, self.category_info[cls].text_image)

                        if self.first_execution or self.log_timer.has_passed(self.seconds_to_log):
                            self.first_execution = False
                            self.__post_log(self.category_info[cls].id, conf)
                            self.log_timer.reset()


                if not detect:
                    self.__clean_lbl()                


                # Resize
                frame_show = imutils.resize(frame_show, width=640)

                # Convertimos el video
                im = Image.fromarray(frame_show)
                img = ImageTk.PhotoImage(image=im)

                # Mostramos en el GUI
                self.lblVideo.configure(image=img)
                self.lblVideo.image = img
                self.lblVideo.after(10, self.__scanning)

            else:
                self.cap.release()
        
    def __post_log(self, category_name, probability):
        timestamp = datetime.now().isoformat()

        requests.post(f"{BASE_API_URL}/waste/waste", json={
            "category_id": category_name,
            "probability": probability,
            "value": "N/A",
            "timestamp": timestamp
        })

# main
def ventana_principal():
    CategoryInference()

if __name__ == "__main__":
    ventana_principal()
