import tkinter as tk
import cv2
from PIL import Image, ImageTk

class VideoApp:
    def __init__(self, window, cap):
        self.window = window
        self.cap = cap
        self.canvas = tk.Canvas(window, width=640, height=480)
        self.canvas.pack()
        self.update_video()

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(frame))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
            self.canvas.image = img
        self.window.after(10, self.update_video)

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)  # Replace with your video source
    root = tk.Tk()
    app = VideoApp(root, cap)
    root.mainloop()
    cap.release()
