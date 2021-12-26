from requests import get, put
from json import loads
from time import sleep
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("hue_config", type=str)
parser.add_argument("hue_username", type=str)
parser.add_argument("action", type=str)
args = parser.parse_args()

class HueLights:
	def __init__(self):
		self.ip = loads(args.hue_config.replace("'", '"'))[0]['internalipaddress']
		self.username = args.hue_username
		self.url = f"http://{self.ip}/api/{self.username}"
		self.lights = loads(get(f"{self.url}/lights").text)
	
	def light_power(self, light, state):
		put(f"{self.url}/lights/{light}/state", json={"on":state})
	
	def all_power(self, state):
		for light in self.lights.keys():
			self.light_power(light, state)
	
	def light_colour(self, light, bri, hue):
		put(f"{self.url}/lights/{light}/state", json={"bri":bri, "hue":hue})

	def all_colour(self, bri, hue):
		for light in self.lights.keys():
			self.light_colour(light, bri, hue)

def default_state(hueObj):
	hueObj.all_colour(150, 45000)

def	power_on(hueObj):
	hueObj.all_power(True)
	default_state(hueObj)

def power_off(hueObj):
	hueObj.all_power(False)

def party_time(hueObj):
	hue_colour = 1000
	timer = 0
	while timer < 25:
		hueObj.all_colour(250, hue_colour)
		hue_colour += 13000
		if hue_colour > 65000:
			hue_colour -= 60000
		timer += 1
		sleep(0.2)
	default_state(hueObj)

def police_time(hueObj):
	red = 1000
	blue = 47000
	timer = 0
	hue_colour = red
	while timer < 10:
		if hue_colour == red:
			hue_colour = blue
		else:
			hue_colour = red
		hueObj.all_colour(200, hue_colour)
		timer += 1
		sleep(0.5)
	default_state(hueObj)

def red_light(hueObj):
	hueObj.all_colour(200, 1000)

def green_light(hueObj):
	hueObj.all_colour(200, 30000)

def blue_light(hueObj):
	hueObj.all_colour(200, 45000)

actionList = {
	"default": default_state,
	"on": power_on,
	"off": power_off,
	"party": party_time,
	"police": police_time,
	"red": red_light,
	"blue": blue_light,
	"green": green_light
}

hue = HueLights()
actionList[args.action](hue)
