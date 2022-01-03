from requests import get, put
from json import load, loads
from time import sleep
import argparse
from functools import partial

# argument passed when calling hueapp.py determines what action is taken
# optional timer argument for effects
parser = argparse.ArgumentParser()
parser.add_argument("action", type=str)
parser.add_argument("-timer", type=int)
args = parser.parse_args()

# hue config json file format
"""
{
	"hue_username": "string",
	"id":"string",
	"internalipaddress":"ip string",
	"port":443
}
"""
with open("hue_config.json") as f:
	hue_config = load(f)

# refer http://web.archive.org/web/20161023150649/http://www.developers.meethue.com:80/documentation/hue-xy-values for colours
# colours loaded in as xy values
with open("colours.json") as f:
	colours = load(f)

class HueLights:
	def __init__(self):
		self.ip = hue_config['internalipaddress']
		self.username = hue_config['hue_username']
		self.url = f"http://{self.ip}/api/{self.username}"
		self.lights = loads(get(f"{self.url}/lights").text)
	
	def light_power(self, light, state):
		put(f"{self.url}/lights/{light}/state", json={"on":state})
	
	def all_power(self, state):
		for light in self.lights.keys():
			self.light_power(light, state)

	def get_colour_state(self):
		statelist = []
		for light in self.lights.keys():
			statelist.append([self.lights[light]['state']['bri'], self.lights[light]['state']['xy']])
		return statelist
	
	def	set_colour_state(self, statelist):
		for light, state in zip(self.lights.keys(), statelist):
			self.light_colour_xy(light, state[0], state[1])
	
	def light_colour_hue(self, light, bri, hue):
		put(f"{self.url}/lights/{light}/state", json={"bri":bri, "hue":hue})
	
	def light_colour_xy(self, light, bri, xy):
		put(f"{self.url}/lights/{light}/state", json={"bri":bri, "xy":xy})

	def all_colour_hue(self, bri, hue):
		for light in self.lights.keys():
			self.light_colour_hue(light, bri, hue)

	def all_colour_xy(self, bri, hue):
		for light in self.lights.keys():
			self.light_colour_xy(light, bri, hue)			

DEF_BRIGHTNESS = 200

def default_state(hueObj):
	hueObj.all_colour_xy(DEF_BRIGHTNESS, colours['blue'])

def	power_on(hueObj):
	hueObj.all_power(True)
	default_state(hueObj)

def power_off(hueObj):
	hueObj.all_power(False)

def party_time(hueObj, timer):
	state = hueObj.get_colour_state()
	hue_colour = 1000
	if timer:
		timer = timer
	else:
		timer = 10
	while timer > 0:
		hueObj.all_colour_hue(DEF_BRIGHTNESS, hue_colour)
		hue_colour += 13000
		if hue_colour > 65000:
			hue_colour -= 60000
		timer -= 1
		sleep(0.2)
	hueObj.set_colour_state(state)

def police_time(hueObj, timer):
	state = hueObj.get_colour_state()
	red = colours['red']
	blue = colours['blue']
	if timer:
		timer = timer
	else:
		timer = 10
	hue_colour = red
	while timer > 0:
		if hue_colour == red:
			hue_colour = blue
		else:
			hue_colour = red
		hueObj.all_colour_xy(DEF_BRIGHTNESS, hue_colour)
		timer -= 1
		sleep(0.5)
	hueObj.set_colour_state(state)

def rainbow(hueObj, timer):
	state = hueObj.get_colour_state()
	rainbow = [
		colours['red'],
		colours['purple'],
		colours['blue'],
		colours['green'],
		colours['yellow'],
		colours['dark orange'],
		colours['magenta']
	]
	if timer:
		timer = timer
	else:
		timer = 14
	while timer > 0:
		for c in rainbow:
			hueObj.all_colour_xy(200, c)
			timer -= 1
			sleep(0.4)
	hueObj.set_colour_state(state)

def rgb_time(hueObj, timer):
	state = hueObj.get_colour_state()
	rgb = [
		colours['red'],
		colours['green'],
		colours['blue']
	]
	if timer:
		timer = timer
	else:
		timer = 10
	while timer > 0:
		for c in rgb:
			hueObj.all_colour_xy(200, c)
			timer -= 1
			sleep(0.2)
	hueObj.set_colour_state(state)	

def all_colour_xy(hueObj, colour):
	hueObj.all_colour_xy(DEF_BRIGHTNESS, colours[colour])

actionList = {
	"default": default_state,
	"on": power_on,
	"off": power_off,
	"party": partial(party_time, timer = args.timer),
	"police": partial(police_time, timer = args.timer),
	"rainbow": partial(rainbow, timer = args.timer),
	"rgb": partial(rgb_time, timer = args.timer)
}

hue = HueLights()
if args.action in colours.keys():
	all_colour_xy(hue, args.action)
else:
	actionList[args.action](hue)
