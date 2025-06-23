
from playsound import playsound
import tkinter as tk
from tkinter import Button
from tkinter import *
from tkinter import ttk
from tkinter import PhotoImage
import time
import threading

#imported the path to mp3 file
def play_sound():
   playsound("C:\\Users\\PRINGCRO\\Desktop\\python\\rascal-flatts-life-is-a-highway.mp3")

#basic layout of window
root = tk.Tk()
root.title("Dyno GUI")
root.configure(background="white")
root.geometry("1100x800+50+50")  

#created a button to actually play music when clicked
my_button = Button(root, text="Click me :D", font=("Arial", 30), bg="red", fg="white", command=play_sound)
my_button.place(x=100, y=600)

#label for incoming voltage data from arduino
info = tk.Label(root, text="Voltage (volts)= ", font=("Arial", 16), width=20, height=4, bd=2, relief="solid")
info.place(x=50, y=100)

#label for current information
moreinfo= tk.Label(root, text="Current (amps)= ", font=("Arial", 16), width=20, height=4, bd=2, relief="solid")
moreinfo.place(x=320, y=100)

#same for power
evenmore = tk.Label(root, text="Power (mW)= ", font=("Arial", 16), width=20, height=4, bd=2, relief="solid")
evenmore.place(x=590, y=100)

#motor efficiency; will code the math; does not use a library
information = tk.Label(root, text="Motor Efficiency= ", font=("Arial", 16), width=20, height=4, bd=2, relief="solid")
information.place(x=590, y=250)

#Title at top of window
title = tk.Label (root, text="Dyno Live Data", font=("Arial", 30))
title.place(x=310, y=25)

#photo of mcqueen
image = PhotoImage(file="C:/Users/PRINGCRO/Desktop/python/car.png")
smaller_image= image.subsample(2,2)
image_label= tk.Label(root,image=smaller_image)
image_label.place(x=590, y=370)

#another amazing photo of mcqueen
image2= PhotoImage(file="C:/Users/PRINGCRO/Desktop/python/car2.png")
smaller_image2=image2.subsample(3,3)
image_label2= tk.Label(root,image=smaller_image2)
image_label2.place(x=850,y=150)


#create outline of graph
canvas = tk.Canvas(root, width=500, height=300, bg="white")
canvas.place(x=50, y=250)

# Draw X and Y axes
canvas.create_line(50, 250, 450, 250, width=2)  # X axis
canvas.create_line(50, 250, 50, 50, width=2)    # Y axis

# Draw grid lines (optional)
for x in range(100, 451, 50):
    canvas.create_line(x, 250, x, 50, fill="#ddd")
for y in range(200, 49, -50):
    canvas.create_line(50, y, 450, y, fill="#ddd")

# Axis labels (optional)
canvas.create_text(460, 250, text="X", font=("Arial", 12))
canvas.create_text(50, 40, text="Y", font=("Arial", 12))

#creates axis title
canvas.create_text(250, 270, text="x-axis title", font=("Arial", 14))   # X-axis title
canvas.create_text(20, 150, text="y-axis title", font=("Arial", 14), angle=90)  # Y-axis title

#graph title
canvas.create_text(250, 30, text="graph title", font=("Arial", 18, "bold"))







#runs 
root.mainloop()

