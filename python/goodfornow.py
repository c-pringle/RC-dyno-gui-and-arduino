from playsound import playsound
import tkinter as tk
from tkinter import Button
from tkinter import *
from tkinter import ttk
from tkinter import PhotoImage
import time
import threading
import serial
import csv
import os
import math 
import subprocess
import platform



ARDUINO_PORT = "COM4"
BAUD_RATE = 9600
SERIAL_TIMEOUT = 1
STALL_TORQUE = 0.028
NO_LOAD_RPM = 12000 * (8.4 / 12)

arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=SERIAL_TIMEOUT)
serial_lock = threading.Lock()

voltage_val = current_val = rpm_val = electrical_power = 0
last_rpm_time = last_voltage_time = last_current_time = last_power_time = time.time()
motor_has_run = False
motor_stopped = False

last_count = 0
last_count_time = time.time()
run_data = []



def open_csv():
    csv_path = "C:/Users/PRINGCRO/Desktop/python/measurements.csv"
    if run_data:
        try:
            torque_str = torque_entry.get().strip()
            if torque_str:
                torque = float(torque_str)
                with open(csv_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Voltage (V)', 'Current (A)', 'Power (W)', 'RPM', 'Efficiency (%)'])
                    for entry in run_data:
                        voltage = entry['voltage']
                        current = entry['current']
                        power = entry['power']
                        rpm = entry['rpm']
                        angular_velocity = 2 * math.pi * rpm / 60
                        mech_power = torque * angular_velocity
                        elec_power = voltage * current
                        efficiency = (mech_power / elec_power) * 100 if elec_power > 0 else 0
                        writer.writerow([voltage, current, power, rpm, efficiency])
                if os.path.exists(csv_path):
                    print("Opening CSV")
                    if platform.system() == "Windows":
                        os.startfile(csv_path)
                    else:
                        print("CSV file is saved but cannot be opened automatically on this OS.")
            else:
                print("Torque input is empty.")
        except Exception as e:
            print(f"Efficiency calculation error: {e}")
    else:
        print("No run data available.")
def reset_data():
    csv_path = "C:/Users/PRINGCRO/Desktop/python/averages.csv"
    header = ['Average Voltage (V)', 'Average Current (A)', 'Average Power (W)', 'Average Motor Efficiency (%)', 'Average RPM']
    
    try:
        with open(csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
        print("CSV file has been reset with only the header row.")
    except Exception as e:
        print(f"Error resetting CSV file: {e}")

    

def safe_serial_write(command):
    with serial_lock:
        arduino.write(command)

def play_sound():
    playsound("C:\\Users\\PRINGCRO\\Desktop\\python\\rascal-flatts-life-is-a-highway.mp3")

root = tk.Tk()
root.title("Dyno GUI")
root.configure(background="white")
root.geometry("1100x1000+50+50")

torque_label = tk.Label(root, text="Enter Torque [Nm]:", font=("Arial", 14))
torque_label.place(x=50, y=700)

torque_entry = tk.Entry(root, font=("Arial", 14), width=10)
torque_entry.place(x=250, y=700)

time_label = tk.Label(root, text="Enter Running Time [sec]:", font=("Arial", 14))
time_label.place(x=50, y=750)

time_entry = tk.Entry(root, font=("Arial", 14), width=10)
time_entry.place(x=300, y=750)

description = tk.Label(root, text="Before clicking start, please input estimated torque and run duration wanted."
                                  "Please wait for the arduino to reset before running again.",
                       font=("Arial", 10), wraplength=500, justify="left")
description.place(x=500, y=25)

my_button = Button(root, text="Click me :D", font=("Arial", 30), bg="red", fg="white", command=play_sound)
my_button.place(x=320, y=267)

info = tk.Label(root, text="Voltage [V]=--", font=("Arial", 14), width=30, height=4, bd=2, relief="solid")
info.place(x=10, y=100)

moreinfo = tk.Label(root, text="Current [A]=--", font=("Arial", 14), width=30, height=4, bd=2, relief="solid")
moreinfo.place(x=320, y=100)

evenmore = tk.Label(root, text="Power [W]=--", font=("Arial", 14), width=30, height=4, bd=2, relief="solid")
evenmore.place(x=650, y=100)

information = tk.Label(root, text="Motor Efficiency=--", font=("Arial", 14), width=45, height=4, bd=2, relief="solid")
information.place(x=590, y=250)

title = tk.Label(root, text="Dyno Live Data", font=("Arial", 30))
title.place(x=200, y=25)

image = PhotoImage(file="C:/Users/PRINGCRO/Desktop/python/car.png")
smaller_image = image.subsample(2, 2)
image_label = tk.Label(root, image=smaller_image)
image_label.place(x=590, y=370)

image2 = PhotoImage(file="C:/Users/PRINGCRO/Desktop/python/car2.png")
smaller_image2 = image2.subsample(3, 3)
image_label2 = tk.Label(root, image=smaller_image2)
image_label2.place(x=20, y=520)

rpm_label = tk.Label(root, text="RPM=--", font=("Arial", 16), width=20, height=4, bd=2, relief="solid")
rpm_label.place(x=50, y=250)

open_csv_button = Button(root, text="Open Averages CSV", font=("Arial", 14), command=open_csv)
open_csv_button.place(x=400, y=700)

reset_data_button = Button(root, text="Reset Data", font=("Arial", 14), command=reset_data)
reset_data_button.place(x=450, y=750)


def reset_serial_connection():
    global arduino
    try:
        arduino.close()
    except:
        pass
    arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=SERIAL_TIMEOUT)

def RUN():
    def task():
        try:
            time_val = time_entry.get().strip()
            if time_val.isdigit():
                command = f"R{time_val}/s\n".encode()
                arduino.write(command)
                print(f"Sent command: {command}")
        except Exception as e:
            print(f"Serial error: {e}")
    threading.Thread(target=task, daemon=True).start()

def reset_motor_values():
    global voltage_val, current_val, rpm_val, electrical_power
    rpm_val = 0
    voltage_val = 0
    current_val = 0
    electrical_power = 0
    rpm_label.config(text="RPM = 0")
    info.config(text="Voltage [V]= 0")
    moreinfo.config(text="Current [A]= 0")
    evenmore.config(text="Power [W]= 0")
    information.config(text="Motor Efficiency= --")
    print("Motor stopped, values reset")

def STOP():
    def task():
        try:
            print("STOP COMMAND")
            arduino.write(b'K\n')
            arduino.write(b"0/v\n")
            arduino.write(b"0/c\n")
            arduino.write(b"0/p\n")
            reset_motor_values()
        except Exception as e:
            print(f"Serial error: {e}")
    threading.Thread(target=task, daemon=True).start()

run = Button(root, text="RUN", font=("Arial", 30), command=RUN)
run.place(x=425, y=400)

stop = Button(root, text="STOP", font=("Arial", 30), command=STOP)
stop.place(x=425, y=500)

run_data= []
def updateState():
    global voltage_val, current_val, rpm_val, electrical_power
    try:
        while arduino.in_waiting:
            line = arduino.readline().decode('utf-8').strip()
            print(f"Received: {line}")

            if line.endswith("/b"):
                value = float(line.split(":")[1].strip().replace("/b", ""))
                global rpm_val
                rpm_val = value
                rpm_label.config(text=f"RPM = {value:.2f}")

            elif line.endswith("/v"):
                value = float(line.split(":")[1].strip().replace("/v", ""))
                voltage_val = value
                info.config(text=f"Voltage [V]= {value:.2f}")

            elif line.endswith("/c"):
                value = float(line.split(":")[1].strip().replace("/c", ""))
                current_val = value
                moreinfo.config(text=f"Current [A]= {value:.2f}")

            elif line.endswith("/p"):
                value = float(line.split(":")[1].strip().replace("/p", ""))
                
                evenmore.config(text=f"Power [W]= {value:.2f}")
                electrical_power = value/1000
                
                run_data.append({
                'rpm' : rpm_val, 'voltage': voltage_val, 'current' : current_val, 'power': electrical_power
            })

                try:
                    torque_str = torque_entry.get().strip()
                    if torque_str:
                        torque = float(torque_str)
                        angular_velocity = 2 * math.pi * rpm_val / 60
                        mech_power_watts = torque * angular_velocity
                        # elec_power_watts = voltage_val * current_val
                        if electrical_power > 0:
                            eff = (mech_power_watts / electrical_power) * 10
                            if eff > 100:
                                print("Warning: Efficiency exceeds 100%. Check units and sensor values.")
                            information.config(text=f"Motor efficiency= {eff:.2f}%")
                            # if eff >= 100.00:
                            #     information.config(text=f"Motor Efficiency= --")
                            # else:
                            #     eff = eff
                        else:
                            information.config(text="Motor Efficiency= --")
                        
                    else:
                        information.config(text="Motor Efficiency= --")
                except Exception as e:
                    print(f"Efficiency calc error: {e}")
                    
        

    except Exception as e:
        print(f"Error reading serial: {e}")
    finally:
        root.after(100, updateState)


root.after(100,updateState)
root.mainloop()
