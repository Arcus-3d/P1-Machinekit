from machinekit import hal
from machinekit import rtapi as rt
from machinekit import config as c


def hardware_read():
    hal.addf('hpg.capture-position', 'servo-thread')
    hal.addf('bb_gpio.read', 'servo-thread')


def hardware_write():
    hal.addf('hpg.update', 'servo-thread')
    hal.addf('bb_gpio.write', 'servo-thread')


def init_hardware():

    # load low-level drivers
    rt.loadrt('hal_bb_gpio', output_pins='807,808,810,819,828,841', input_pins='809,831,832,833,835,837,838')
    prubin = '%s/%s' % (c.Config().EMC2_RTLIB_DIR, c.find('PRUCONF', 'PRUBIN'))
    rt.loadrt(c.find('PRUCONF', 'DRIVER'), pru=0, num_stepgens=4, num_pwmgens=4, pru_period=2500, prucode=prubin, halname='hpg')

    # Python user-mode HAL module to read ADC value and generate a thermostat output for PWM
    #hal.loadusr('hal_adc_value',name='vac_sense',interval=0.10,filter_size=2,channels='01:0.075:57.47',wait_name='vac_sense')

def setup_hardware(thread):
    # PWM
    hal.Pin('hpg.pwmgen.00.pwm_period').set(6250000)  # 400Hz?
    hal.Pin('hpg.pwmgen.00.out.00.pin').set(836)  # rotate
    hal.Pin('hpg.pwmgen.00.out.01.pin').set(840)  # mirror
    hal.Pin('hpg.pwmgen.00.out.02.pin').set(845)  # valve
    hal.Pin('hpg.pwmgen.00.out.03.pin').set(846)  # light

    hal.Pin('hpg.pwmgen.00.out.02.enable').link('emcmot-0-enable')
    hal.Pin('hpg.pwmgen.00.out.02.value').link('valve-pwm')
    hal.Pin('motion.analog-out-io-25').link('valve-pwm')
    
    hal.Pin('hpg.pwmgen.00.out.03.enable').link('emcmot-0-enable')
    hal.Pin('hpg.pwmgen.00.out.03.value').link('light-pwm')
    hal.Pin('motion.analog-out-io-26').link('light-pwm')

    # hal.Signal('f%i-pwm-enable' % n).set(True)

    # configure hotend cooling fan
    #hal.Pin('hpg.pwmgen.00.out.05.enable').link('exp0-pwm-enable')
    #hal.Pin('hpg.pwmgen.00.out.05.value').set(1.0)
    #hal.Pin('hpg.pwmgen.00.out.05.value').link('exp0-pwm')
    # configure leds
    # none

    # GPIO
    # Undo stuff
    hal.Pin('axis.0.home-sw-in').unlink()
    hal.Pin('axis.1.home-sw-in').unlink()
    hal.Pin('axis.2.home-sw-in').unlink()
    # do it myself
    hal.Pin('axis.0.home-sw-in').link('limit-0-home')
    hal.Pin('axis.1.home-sw-in').link('limit-0-home')
    hal.Pin('axis.2.home-sw-in').link('limit-0-home')
    # link
    hal.Pin('bb_gpio.p8.in-35').link('limit-0-home')  
    # probe ...
    hal.Pin('bb_gpio.p8.in-31').link('probe-signal')    

    # Adjust as needed for your switch polarity
    hal.Pin('bb_gpio.p8.in-31.invert').set(False)
    #hal.Pin('bb_gpio.p8.in-32.invert').set(False)
    hal.Pin('bb_gpio.p8.in-35.invert').set(True)
    #hal.Pin('bb_gpio.p8.in-33.invert').set(False)
    hal.Pin('bb_gpio.p8.in-38.invert').set(False)
    #hal.Pin('bb_gpio.p8.in-37.invert').set(False)

    # ADC
    #hal.Pin('vac_sense.ch-01.value').link('vac-measure')

    # Stepper
    hal.Pin('hpg.stepgen.00.steppin').set(842)
    hal.Pin('hpg.stepgen.00.dirpin').set(839)
    hal.Pin('hpg.stepgen.01.steppin').set(843)
    hal.Pin('hpg.stepgen.01.dirpin').set(844)
    hal.Pin('hpg.stepgen.02.steppin').set(827)
    hal.Pin('hpg.stepgen.02.dirpin').set(829)
    hal.Pin('hpg.stepgen.03.steppin').set(830)
    hal.Pin('hpg.stepgen.03.dirpin').set(834)

    # axis enable signals
    # Using one pin to enable all axis
    hal.Pin('bb_gpio.p8.out-41').link('emcmot-0-enable')
    hal.Pin('bb_gpio.p8.out-41.invert').set(True)
    #hal.Pin('bb_gpio.p8.out-40').link('emcmot-1-enable')
    #hal.Pin('bb_gpio.p8.out-40.invert').set(True)
    #hal.Pin('bb_gpio.p8.out-28').link('emcmot-2-enable')
    #hal.Pin('bb_gpio.p8.out-28.invert').set(True)
    #hal.Pin('bb_gpio.p8.out-19').link('emcmot-3-enable')
    #hal.Pin('bb_gpio.p8.out-19.invert').set(True)

    # Machine power 
    hal.Pin('bb_gpio.p8.out-08').link('estop-loop')
    hal.Pin('bb_gpio.p8.in-09').link('estop-in')
    #hal.Pin('bb_gpio.p8.in-09.invert').set(True)
    hal.Pin('bb_gpio.p8.out-07').link('estop-out')
    hal.Pin('bb_gpio.p8.out-07.invert').set(True)

    # Tie machine power signal to the BeBoPr LED
    # Feel free to tie any other signal you like to the LED
    hal.Pin('bb_gpio.p8.out-10').link('emcmot-0-enable')


def setup_exp(name):
    hal.newsig('%s-pwm' % name, hal.HAL_FLOAT, init=0.0)
    hal.newsig('%s-pwm-enable' % name, hal.HAL_BIT, init=False)
