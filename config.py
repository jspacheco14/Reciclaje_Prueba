from dataclasses import dataclass
from PIL import Image
import cv2
import numpy as np
from datetime import datetime
import requests

BASE_API_URL = "http://localhost:8000"

class CategoryNames:
    metal='Metal'
    glass="Glass"
    plastic="Plastic"
    carton="Carton"
    medical="Medical"

@dataclass
class Point:
    x: int = 0
    y: int = 0

    def get_tuple(self):
        return (self.x, self.y)
    
    def __setattr__(self, name, value):
        if value < 0: value = 0
        super().__setattr__(name, int(value))

@dataclass
class WasteCategoryInformation:
    id: str
    name: str
    color: tuple[int]
    visual_image: Image
    text_image: Image

def get_image(path: str) -> Image:
    img = cv2.imread(path)

    img = np.array(img, dtype="uint8")
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = Image.fromarray(img)

    return img


def get_categories_information():
    response_data = requests.get(f"{BASE_API_URL}/waste/category")
    json_data:dict[str, object] = response_data.json()

    final_data: dict[int, WasteCategoryInformation] = {}
    for item in json_data:
        if item["name"] == CategoryNames.metal:
            final_data[0] = WasteCategoryInformation(item.get("id"), CategoryNames.metal, color=(255,255,0), text_image=get_image("setUp/metaltxt.png"), visual_image=get_image("setUp/metal.png"))
        if item["name"] == CategoryNames.glass:
            final_data[1] = WasteCategoryInformation(item.get("id"), CategoryNames.glass, color=(255, 255, 255), text_image=get_image("setUp/vidriotxt.png"), visual_image=get_image("setUp/vidrio.png"))
        if item["name"] == CategoryNames.plastic:
            final_data[2] = WasteCategoryInformation(item.get("id"), CategoryNames.plastic, color=(0, 0, 255), text_image=get_image("setUp/plasticotxt.png"), visual_image=get_image("setUp/plastico.png"))
        if item["name"] == CategoryNames.carton:
            final_data[3] = WasteCategoryInformation(item.get("id"), CategoryNames.carton, color=(150, 150, 150), text_image=get_image("setUp/cartontxt.png"), visual_image=get_image("setUp/carton.png"))
        if item["name"] == CategoryNames.medical:
            final_data[4] = WasteCategoryInformation(item.get("id"), CategoryNames.medical, color=(255, 0, 0), text_image=get_image("setUp/medicaltxt.png"), visual_image=get_image("setUp/medical.png"))
    
    return final_data

class Timer:
    def __init__(self):
        self._start_time = datetime.now()

    def seconds_elapsed(self) -> float:
        """Return the number of seconds elapsed since the last reset."""
        now = datetime.now()
        elapsed = (now - self._start_time).total_seconds()
        return elapsed
    
    def has_passed(self, t: int) -> bool:
        return self.seconds_elapsed() >= t

    def reset(self):
        """Reset the timer to the current time."""
        self._start_time = datetime.now()