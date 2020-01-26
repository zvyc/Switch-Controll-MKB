import pygame

from switchlib import InputManager
from seriallib import Payload

class Control:
	def __init__(self):
		self.KeyConfig = InputManager("KeyMapping/minecraft.csv")
		self.mappingDict = self.KeyConfig.mappingDict
		self.payload = Payload()

		self.winDim = (1024, 720)
		self.mouseSens = (4, 4)
		self.mouseDelta = (0, 0)
		title = "Key Input Retriever"

		pygame.init()
		pygame.display.set_caption(title)

		self.screen = pygame.display.set_mode(self.winDim)

		self.myFont = pygame.font.SysFont("Arial", 16, bold=True)

		self.textColor = pygame.Color(255, 255, 255)
		self.screenFillColor = pygame.Color(0, 0, 0)

	def readPortAsIntArr(self, ser) -> tuple:
	    serialBytes = ser.read_all()
	    intArray = []
	    for singleByte in serialBytes:
	        if type(singleByte) == int:
	            intArray.append(singleByte)
	        else:
	            intArray.append(int.from_bytes(singleByte, byteorder="big"))
	    return tuple(intArray)

	def sendInput(self, ser, keysDown, pause_script, lockMouse):
			self.payload.resetAllInputs()
			self.keysDown = keysDown.copy()
			for event in pygame.event.get():
				pygame.event.pump()
				if event.type == pygame.QUIT:
					return "exit"
				
				elif event.type == pygame.MOUSEMOTION:
					self.mouseDelta = event.rel

				elif event.type == pygame.MOUSEBUTTONDOWN:
					keyStr = f"m{event.button}"
					if not keyStr in self.keysDown:
						print("adding:", f"m{event.button}")
						self.keysDown.append(keyStr)

				# elif event.type == pygame.MOUSEBUTTONUP:
				# 	keyStr = f"m{event.button}"
				# 	if keyStr in keysDown:
				# 		print("removing:", f"m{event.button}")
				# 		keysDown.remove(keyStr)

			if pause_script == False:
				self.KeyConfig.processInputs(self.payload, self.keysDown, (self.mouseDelta[0] * self.mouseSens[0], self.mouseDelta[1] * self.mouseSens[1]))
			else:
				#keysDown = [self.mappingDict[x][0] for x in keysDown]
				#print(keysDown)
				self.KeyConfig.processInputs(self.payload, self.keysDown, (0, 0))

			if lockMouse and pygame.mouse.get_focused():
					pygame.mouse.set_pos(self.winDim[0] / 2, self.winDim[1] / 2)
					pygame.event.get(pygame.MOUSEMOTION)
			self.mouseDelta = (0, 0)

			self.screen.fill(self.screenFillColor)

			self.screen.blit(self.myFont.render(f"Sending:{str(self.payload)}", True, self.textColor), (0,0))
			self.screen.blit(self.myFont.render(f"Receiving:{self.readPortAsIntArr(ser)}", True, self.textColor), (0,20))

			pygame.display.flip()
			if pygame.mouse.get_focused() == False and pause_script == False:
				ser.write(bytearray([128, 128, 128, 128, 8, 0, 0]))
			else:
				ser.write(self.payload.asByteArray())

			return "success"

	def quit(self):
		pygame.quit()
