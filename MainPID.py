import pidcontrol
import cv2
import pyvisa
import Procedures as proc
import time
import collections
import keyboard

stop = False
start_up = True

main_queue = collections.deque(['Init','Init'], maxlen = 2)
setpoint_queue = collections.deque([0,0], maxlen = 2)

k1 = 0
k2 = 0
t_ramp_min = 1
loop_counter = 0
POWER_CHECK_COUNTER = 30
ARDUINO_ANALOG_CHANNEL = 1
LINE_VOLTAGE_THRESHOLD = 10


while stop != True:

    t0 = time.time()*1000

    loop_counter += 1

    ####################################################
    if main_queue[0] == 'Init':

        # load ini file
        ini = proc.ini_file('basic.ini')

        coefs_tup = (ini.kp, ini.ki, ini.kd)
        range_tup = (0, 100)

        # chose GPIB visa instrument for TC input (Keithley 2110)
        inst = proc.define_TC_input()

        # chose ramp mode Temperature gradient/ConstPower
        in_line = ''
        while True:
            in_line = input("Enter ramp mode: TempGradient (T) / Constant Power (P)")
            print(in_line)
            if (in_line == 'T') or (in_line == 'P') or (in_line == 'p') or (in_line == 't'):
                break

        if in_line == 'T' or in_line == 't':
            main_queue[0] = 'RampT'
            main_queue[1] = 'PID'
        elif in_line == 'P' or in_line == 'p':
            main_queue[0] = 'ConstPower'
            main_queue[1] = 'ConstPower'
        else:
            pass

        ss, setpoint = proc.input_float('Enter temperature setpoint (Celsius)')
        setpoint_queue.append(setpoint)

        if main_queue[0] == 'ConstPower':
            ss, const_power = proc.input_float('Enter ramp power (%)')

        if main_queue[0] == 'RampT':
            ss, t_ramp_min = proc.input_float('Enter ramp time (min)')
            t_start_ramp = time.time()*1000

        if start_up:
            PID = pidcontrol.PIDClass(coefs_tup, setpoint_queue[0], range_tup,
                                      integration_samples=ini.integration_samples ,
                                      diff_filter_samples=ini.diff_filter_samples )
            arduino = proc.ArduinoClass(port = ini.port, main_heater_channel=ini.d_channel,
                                        aux_heater_channel=ini.aux_channel, analog_channel=ini.analog_channel)
            print('Wait for initialization...')
            time.sleep(5)
            arduino.aux_relay_on()
            print('StartUP done. AUX relay on')
            start_up = False
        else:
            PID.set_coefs(coefs_tup)



    ####################################################################
    elif main_queue[0] == 'PID':
        t1 = time.time()*1000
        curr_temp = float(inst.query("MEAS:TCOuple?")[:15])
        t2 = time.time()*1000
        pid_value = PID.control(t2, curr_temp)
        #print('PID output '+str(pid_value))
        t3 = time.time()*1000
        pulse_width = (ini.pid_loop_period_ms - (t3 - t0)) * pid_value/100
        if pulse_width > 0:
            arduino.heater_on()
        k1 = cv2.waitKey(int(pulse_width))
        arduino.heater_off()
        empty_width = ini.pid_loop_period_ms - (t3 - t0) - pulse_width
        k2 = cv2.waitKey(int(empty_width))
        print("PID. Current temperature: "+ str(curr_temp))

        if main_queue[1] == 'RampT':
            main_queue.append('PID')
            print('PID: RAMP-PID')


    elif main_queue[0] == 'RampT':

        if setpoint_queue[1] - setpoint_queue[0] > 1:
            t_curr = time.time() * 1000
            t_ramp_ms = t_ramp_min * 60 * 1000
            setpoint_queue[0] = setpoint_queue[1] * (t_curr - t_start_ramp) / t_ramp_ms
            PID.setpoint(setpoint_queue[0])
            main_queue.append('RampT')
            print('RampT. Local Tsp '+str(setpoint_queue[0]))
            print('RAMP: RAMP-PID')
        else:
            main_queue.append('PID')
            main_queue.append('PID')
            setpoint_queue[0] = setpoint_queue[1]
            PID.setpoint(setpoint_queue[0])
            print('RAMP: PID-PID - temperature reached')

    elif main_queue[0] == 'ConstPower':
        t1 = time.time() * 1000
        curr_temp = float(inst.query("MEAS:TCOuple?")[:15])
        t2 = time.time() * 1000
        c_power_length = const_power * ini.pid_loop_period_ms
        t3 = time.time() * 1000
        pulse_width = (ini.pid_loop_period_ms - (t3-t0))*const_power/100
        arduino.heater_on()
        k1 = cv2.waitKey(int(pulse_width))
        arduino.heater_off()
        empty_width = ini.pid_loop_period_ms - (t3 - t0) - pulse_width
        k2 = cv2.waitKey(int(empty_width))
        print("Current temperature: " + str(curr_temp))

        if curr_temp >= setpoint_queue[1]:
            main_queue.append('PID')
            main_queue.append('PID')
            setpoint_queue[0] = setpoint_queue[1]
            PID.setpoint(setpoint_queue[0])
            print('Const power: PID-PID - temperature reached')

    else:
        pass

    # measure the voltage in the main power line
    if loop_counter >= POWER_CHECK_COUNTER:
        line_voltage = arduino.read_line_voltage(ARDUINO_ANALOG_CHANNEL)
        if line_voltage < LINE_VOLTAGE_THRESHOLD:
            arduino.aux_relay_off()
            stop = True
            print('Line voltage is below the threshold. AUX relay off. Controller stops')
            print(time.localtime())
        else:
            loop_counter = 0

    k3 = cv2.waitKey(1)

    if keyboard.is_pressed(" "):
        s = input('Chose mode: E - exit, P - PID-control, I - initialization')
        s = s.upper()
        if s == 'E':
            stop = True
        elif s == 'P':
            main_queue.append('RampT')
            main_queue.append('PID')

        elif s == 'I':
            main_queue.append('Init')
            main_queue.append('Init')
        else:
            main_queue.append('PID')
            main_queue.append('PID')


arduino.close_serial()
inst.close()