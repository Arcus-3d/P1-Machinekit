import os

from machinekit import rtapi as rt
from machinekit import hal
from machinekit import config as c

from fdm.config import base
from fdm.config import storage
from fdm.config import motion
import bebopr as hardware
import rc_servo as servo

# initialize the RTAPI command client
rt.init_RTAPI()
# loads the ini file passed by linuxcnc
c.load_ini(os.environ['INI_FILE_NAME'])

motion.setup_motion(kinematics='itripodkins')
hal.Pin('itripodkins.Bx').set(c.find('MACHINE', 'TRIPOD_BX'))
hal.Pin('itripodkins.Cx').set(c.find('MACHINE', 'TRIPOD_CX'))
hal.Pin('itripodkins.Cy').set(c.find('MACHINE', 'TRIPOD_CY'))

hardware.init_hardware()
storage.init_storage('storage.ini')

# reading functions
hardware.hardware_read()
hal.addf('motion-command-handler', 'servo-thread')
hal.addf('motion-controller', 'servo-thread')
# Axis-of-motion Specific Configs (not the GUI)
# XYZ axes
for i in range(3):
    base.setup_stepper(section='AXIS_%i' % i, axisIndex=i, stepgenIndex=i, thread='servo-thread')

servo.setup_servo_axis(servoIndex=0,section='AXIS_5',axisIndex=5,pwm='hpg.pwmgen.00.out.00', thread='servo-thread')
servo.setup_servo_axis(servoIndex=1,section='AXIS_3',axisIndex=3,pwm='hpg.pwmgen.00.out.01', thread='servo-thread')
#hal.Pin('motion.digital-out-10').link('mirror-deploy')
#servo.setup_servo_toggle(servoIndex=1,section='MIRROR',pwm='hpg.pwmgen.00.out.01', selectSignal='mirror-deploy', thread='servo-thread')

#errorSignals = ['temp-hw-error', 'watchdog-error', 'hbp-error']
errorSignals = []
base.setup_estop(errorSignals, thread='servo-thread')
base.setup_tool_loopback()
# Probe
base.setup_probe(thread='servo-thread')
# Setup Hardware
hardware.setup_hardware(thread='servo-thread')


# write out functions
hardware.hardware_write()

# read storage.ini
storage.read_storage()

# start haltalk server after everything is initialized
# else binding the remote components on the UI might fail
#hal.loadusr('haltalk', wait=True)
hal.loadusr('linuxcncrsh')
