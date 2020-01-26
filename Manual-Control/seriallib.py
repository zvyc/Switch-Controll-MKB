from maths import clamp, clamp_mouse_coords
from JoystickEnums import Button, Stick, HAT

class Payload:
    """
    Serial data payload class to handle controller serial data in order
    to prevent errors from input.
    """
    MAX_BUTTON_VALUE = 16383

    def __init__(self):
        self.leftStick = (Stick.CENTER.value, Stick.CENTER.value)
        self.rightStick = (Stick.CENTER.value, Stick.CENTER.value)
        self.hat = HAT.CENTER.value
        self.buttons = 0

    def __repr__(self):
        return f"{self.__dict__}"

    def __str__(self):
        button_list = [button.name
                       for ind, button in enumerate(Button)
                       if self.buttons & (1 << ind)]
        st = f"LeftStick: {self.leftStick}, RightStick: {self.rightStick}," + \
             f"HAT: {HAT(self.hat).name}, Buttons: {button_list}"
        return st

    def setLeftX(self, x: int) -> None:
        self.leftStick = (clamp_mouse_coords(x, Stick.MIN.value, Stick.MAX.value), 
                        self.leftStick[1])

    def setLeftY(self, y: int) -> None:
        self.leftStick = (self.leftStick[0], 
                        clamp_mouse_coords(y, Stick.MIN.value, Stick.MAX.value))

    def setLeftStick(self, x: int, y: int) -> None:
        self.leftStick = (clamp(x, Stick.MIN.value, Stick.MAX.value),
                            clamp(y, Stick.MIN.value, Stick.MAX.value))

    def setRightX(self, x: int) -> None:
        self.rightStick = (clamp_mouse_coords(x, Stick.MIN.value, Stick.MAX.value),
                        self.rightStick[1])

    def setRightY(self, y: int) -> None:
        self.rightStick = (self.rightStick[0], clamp_mouse_coords(y, Stick.MIN.value, Stick.MAX.value))

    def setRightStick(self, x: int, y: int) -> None:
        self.rightStick = (clamp(x, Stick.MIN.value, Stick.MAX.value),
                           clamp(y, Stick.MIN.value, Stick.MAX.value))

    def setHatFromVector(self, x, y) -> None:
        dPadList = [
            [7, 0, 1],
            [6, 8, 2],
            [5, 4, 3]
        ]
        self.hat = dPadList[y + 1][x + 1]

    def applyButtons(self, *args: Button) -> None:
        if not len(args) > 0:
            return
        for item in args:
            if type(item) == Button:
                value = item.value
            else:
                value = item
            self.buttons |= value
        self.buttons = clamp(self.buttons, 0, self.MAX_BUTTON_VALUE)

    def unapplyAllButtons(self) -> None:
        self.buttons = 0

    def resetAllInputs(self) -> None:
        self.leftStick = (Stick.CENTER.value, Stick.CENTER.value)
        self.rightStick = (Stick.CENTER.value, Stick.CENTER.value)
        self.buttons = 0
        self.hat = HAT.CENTER.value

    def asByteArray(self) -> bytearray:
        buttons1, buttons2 = (b for b in self.buttons.to_bytes(2, byteorder="little"))
        return bytearray([self.leftStick[0], self.leftStick[1],
                          self.rightStick[0], self.rightStick[1],
                          self.hat, buttons1, buttons2])
