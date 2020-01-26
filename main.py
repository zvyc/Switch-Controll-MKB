import serial
import threading
import sys
import time

from pynput.keyboard import Listener as KeyboardListener
from pynput.keyboard import Key
from serial.tools import list_ports

sys.path.append('Manual-Control')

import switch
from constants import KeyToIntDict

quit_key = '+'
pause_key = ','

pause_script = False
quit = False
lockMouse = False
keysDown = []
UPDATES_PER_SECOND = 60
ser = None
times_ran_instructions = 0

def getPortFromUser():
	portList = list(list_ports.grep(""))
	if len(portList) == 0:
		raise LookupError("Unable to detect Serial Device.")
	indexPortListString = [f"Device Port: {port.device}, Device Description: {port.description}"
						   for _, port in enumerate(portList)]
	print(indexPortListString)
	return portList[0].device

def on_press(key):
	global pause_script
	global quit
	global lockMouse
	global times_ran_instructions

	try: pressed_key = ord(key.char.lower())
	except:
		try:
			pressed_key = KeyToIntDict[key]
		except KeyError:
			print('Error converting key: ', key, ' to integer')
			return True

	if chr(pressed_key) == pause_key or pressed_key == 16:
		print("User pressed the pause key '" + pause_key + "', pausing/unpausing manual control")
		times_ran_instructions = 0
		pause_script = not pause_script

	if chr(pressed_key) == quit_key or quit == True:
		print("User pressed the key '" + quit_key + "', quitting the script")
		quit = True
		return False

	if pressed_key == 9:
		lockMouse = not lockMouse

	if pressed_key not in keysDown and pause_script == False:
		keysDown.append(pressed_key)

def on_release(key):
	global pause_script
	try: pressed_key = ord(key.char.lower())
	except:
		try:
			pressed_key = KeyToIntDict[key]
		except KeyError:
			print('Error converting key: ', key, ' to integer')
			return True

	if pressed_key in keysDown:
		keysDown.remove(pressed_key)

def input_listen():
	with KeyboardListener(on_press=on_press, on_release=on_release) as listener:
		listener.join()

def run_instructions_from_txt(filepath, control):
	global pause_script
	global quit
	global keysDown
	global lockMouse
	global ser
	global times_ran_instructions

	with open(filepath, 'r') as file:
		#instructions = []
		content = file.readlines()
		for instruction in content:
			if instruction == "\n" or instruction == "":
				continue
			instruction_list = instruction.strip().split(': ')
			if ", " in instruction_list[1]:
				instruction_list = instruction_list[:1] + instruction_list[1:][0].split(', ')

			if instruction_list[0] == "duration" or (times_ran_instructions == 0 and instruction_list[0] == "!duration"):
				print("duration: ", float(instruction_list[1]))
				time.sleep(float(instruction_list[1]))

			keysDown = []
			if instruction_list[0] == 'delay' or (times_ran_instructions == 0 and instruction_list[0] == "!delay"):
				res = control.sendInput(ser, keysDown, pause_script, lockMouse)
				print("delay: ", float(instruction_list[1]))
				time.sleep(float(instruction_list[1]))
				if res == "exit": quit = True

			elif instruction_list[0] == 'press' or (times_ran_instructions == 0 and instruction_list[0] == "!press"):
				for key in instruction_list[1:]:
					keysDown.append(key)

				print("press: ", keysDown)
				res = control.sendInput(ser, keysDown, pause_script, lockMouse)
				if res == "exit": quit = True

			if quit == True or pause_script == False:
				return
		times_ran_instructions += 1

			#instructions.append(instruction_list)
		#return instructions

def run_instructions(instructions, control):
	global pause_script
	global quit
	global keysDown
	global lockMouse
	global ser

	for index, instruction in enumerate(instructions):
		keysDown = []
		if instruction[0] == 'delay':
			res = control.sendInput(ser, keysDown, pause_script, lockMouse)
			time.sleep(float(instruction[1]))
			if res == "exit": quit = True

		elif instruction[0] == 'press':
			if len(instruction) > 2:
				for key in instruction[1:]:
					keysDown.append(key)
			else:
				keysDown.append(instruction[1])

			res = control.sendInput(ser, keysDown, pause_script, lockMouse)
			if instructions[index + 1][0] == "duration":
				time.sleep(float(instructions[index + 1][1]))
			if res == "exit": quit = True

def switch_control():
	global pause_script
	global quit
	global keysDown
	global lockMouse
	global ser

	ser = serial.Serial(getPortFromUser(), 38400, writeTimeout = 0)
	control = switch.Control()

	while(True):
		if pause_script == False:
			res = control.sendInput(ser, keysDown, pause_script, lockMouse)
			if res == "exit": quit = True
		else:
			run_instructions_from_txt('auto.txt', control)

		if quit == True:
			ser.write(bytearray([128, 128, 128, 128, 8, 0, 0])) # Resets all inputs
			ser.flush()
			ser.close()
			control.quit()
			break

		time.sleep(1/UPDATES_PER_SECOND)
	print('switch_control function finished')

if __name__ == "__main__":
	switch_control = threading.Thread(target=switch_control)
	switch_control.daemon = False  
	switch_control.start()	

	input_listen = threading.Thread(target=input_listen)
	input_listen.daemon = False  
	input_listen.start()
