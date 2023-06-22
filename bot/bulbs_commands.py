import time
from yeelight import Bulb, discover_bulbs


def is_all_off(my_bulbs):
    power_level = 0
    for i in range(len(my_bulbs)):
        power = my_bulbs[i]['capabilities']['power']
        if power == 'on':
            power_level += 1
    if power_level != 0:
        return False
    else:
        return True


def connection():
    try:
        my_bulbs = discover_bulbs()
        if len(my_bulbs) == 0:
            raise Exception("Can't connect")
    except Exception as e:
        print(e)
        return e
    while len(my_bulbs) != 2:
        my_bulbs = discover_bulbs()
        time.sleep(1)
    return my_bulbs


def all_on(my_bulbs):
    for ip_bulb in my_bulbs:
        bulb = Bulb(ip_bulb['ip'])
        bulb.turn_on()


def all_off(my_bulbs):
    for ip_bulb in my_bulbs:
        bulb = Bulb(ip_bulb['ip'])
        bulb.turn_off()


def show_all(my_bulbs):
    All_bulbs = []
    for i in range(len(my_bulbs)):
        power = my_bulbs[i]['capabilities']['power']
        All_bulbs.append("Bulb #" + str(i + 1) + ": power_mode:" + power)
    return All_bulbs


def set_brightness(my_bulbs, brightness):
    for ip_bulb in my_bulbs:
        bulb = Bulb(ip_bulb['ip'], auto_on=True)
        bulb.set_brightness(int(brightness))


def dif_on(my_bulbs, num):
    ip_bulb = my_bulbs[int(num) - 1]
    bulb = Bulb(ip_bulb['ip'])
    bulb.turn_on()


def dif_off(my_bulbs, num):
    ip_bulb = my_bulbs[int(num) - 1]
    bulb = Bulb(ip_bulb['ip'])
    bulb.turn_off()


def set_mode(my_bulbs):
    ip_bulb1 = my_bulbs[0]
    ip_bulb2 = my_bulbs[1]
    bulb1 = Bulb(ip_bulb1['ip'], effect='smooth', duration=400, auto_on=True)
    bulb2 = Bulb(ip_bulb2['ip'], effect='smooth', duration=400, auto_on=True)
    for i in range(30):
        bulb1.turn_off()
        bulb2.turn_off()
        time.sleep(0.5)
        bulb1.turn_on()
        bulb2.turn_on()
