import pidcontrol
import cv2
import pyvisa
import serial
import array
import configparser


class ini_file():
    """class to create the object which reads settings from ini file and makes them its own properties"""

    def __init__(self, inifilename):

        config = configparser.ConfigParser()
        config.read(inifilename)

        self.sections = config.sections()

        for sec in self.sections:
            for k in config[sec].keys():
                exec('setattr(self,k,' + config[sec][k] + ')')


class ArduinoClass():

    def __init__(self, port = 'COM5', d_channel = 2):

        self.usbport = port
        self.channel = d_channel

        # initialize serial port
        self.ser = serial.Serial(self.usbport, 9600, timeout=1)

        self.heater_off()

    def heater_off(self):
        ar = array.array('B', [254, self.channel, 0]).tobytes()
        self.ser.write(ar)

    def heater_on(self):
        ar = array.array('B', [254, self.channel, 1]).tobytes()
        self.ser.write(ar)

    def close_serial(self):
        self.ser.close()
        print('port released')


def define_TC_input():
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    visa_name = input("Enter visa resource name : ")
    print("visa name : " + visa_name)
    inst = rm.open_resource(visa_name)
    print(inst.query("*IDN?"))
    inst.write("TCOuple:TYPE K")
    return inst

def try_to_float(s):
    res = -999
    try:
        res = float(s)
        ss = True
    except:
        print('Not a number')
        ss = False

    return ss,res

def input_float(t):
    res = -999
    ss = False
    while ss != True:
        in_line = input(t+': ')
        ss, res = try_to_float(in_line)

    return ss,res