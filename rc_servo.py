from machinekit import hal
from machinekit import rtapi as rt
from machinekit import config as c

def setup_servo_axis(servoIndex, section, axisIndex, pwm, thread=None):
    servo = '%s.%02i' % ('rc_servo', servoIndex)
    scale = rt.newinst('scale', '%s-scale' % servo)
    hal.addf(scale.name, thread)
    limit1 = rt.newinst('limit1', '%s-limit' % servo)
    hal.addf(limit1.name, thread)
    
    enable = hal.newsig('emcmot-%i-enable' % axisIndex, hal.HAL_BIT)
    enable.set(False);
    hal.Pin('%s.enable' % pwm).link(enable)
    
    scale.pin('out').link(limit1.pin('in'))
    
    pwmout = hal.newsig('%s-pwm-out' % servo, hal.HAL_FLOAT)
    limit1.pin('out').link(pwmout)
    hal.Pin('%s.value' % pwm).link(pwmout)
    axis = 'axis.%i' % axisIndex
    enable = hal.Signal('emcmot-%i-enable' % axisIndex, hal.HAL_BIT)
    enable.link('%s.amp-enable-out' % axis)

    # expose timing parameters so we can multiplex them later
    sigBase = 'rc-servo-%i' % servoIndex
    scale = hal.newsig('%s-scale' % sigBase, hal.HAL_FLOAT)
    offset = hal.newsig('%s-offset' % sigBase, hal.HAL_FLOAT)
    smin = hal.newsig('%s-min' % sigBase, hal.HAL_FLOAT)
    smax = hal.newsig('%s-max' % sigBase, hal.HAL_FLOAT)

    hal.Pin('%s-scale.gain' % servo).link(scale)
    hal.Pin('%s-scale.offset' % servo).link(offset)
    hal.Pin('%s-limit.min' % servo).link(smin)
    hal.Pin('%s-limit.max' % servo).link(smax)
    scale.set(c.find(section, 'SCALE',0.000055556))
    offset.set(c.find(section, 'SERVO_OFFSET',.003))
    smin.set(c.find(section, 'SERVO_MIN',0.02))
    smax.set(c.find(section, 'SERVO_MAX',0.04))

    posCmd = hal.newsig('emcmot-%i-pos-cmd' % axisIndex, hal.HAL_FLOAT)
    posCmd.link('%s.motor-pos-cmd' % axis)
    posCmd.link('%s-scale.in' % servo)
    posCmd.link('%s.motor-pos-fb' % axis)
    limitHome = hal.newsig('limit-%i-home' % axisIndex, hal.HAL_BIT)
    limitMin = hal.newsig('limit-%i-min' % axisIndex, hal.HAL_BIT)
    limitMax = hal.newsig('limit-%i-max' % axisIndex, hal.HAL_BIT)
    limitHome.link('%s.home-sw-in' % axis)
    limitMin.link('%s.neg-lim-sw-in' % axis)
    limitMax.link('%s.pos-lim-sw-in' % axis)
def setup_servo_toggle(servoIndex, section, pwm, selectSignal,thread=None):
    servo = '%s.%02i' % ('rc_servo', servoIndex)
    mux2 = rt.newinst('mux2', '%s-mux2' % servo)
    hal.addf(mux2.name, thread)
    pwmout = hal.newsig('%s-pwm-out' % servo, hal.HAL_FLOAT)
    mux2.pin('out').link(pwmout)
    hal.Pin('%s.value' % pwm).link(pwmout)
    enable = hal.Signal('emcmot-0-enable', hal.HAL_BIT)
    hal.Pin('%s.enable' % pwm).link(enable)
    
    sigBase = 'rc-servo-%i' % servoIndex
    smin = hal.newsig('%s-min' % sigBase, hal.HAL_FLOAT)
    smax = hal.newsig('%s-max' % sigBase, hal.HAL_FLOAT)

    hal.Pin('%s-mux2.in1' % servo).link(smin)
    hal.Pin('%s-mux2.in0' % servo).link(smax)
    smin.set(c.find(section, 'SERVO_MIN',0.1))
    smax.set(c.find(section, 'SERVO_MAX',0.2))
    mux2.pin('sel').link('%s' % selectSignal)
