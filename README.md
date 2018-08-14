
# G.A.L

This python app is intended to be used as a game "library" or archiver, it will organize games in lists, those will be navigable using a gamepad. This app is only available for GNU/Linux distributions using Xorg as window server since it makes an intensive use of python Xlib.


### Prerequisites
To run this app you will need any GNU/Linux distribution using [Xorg](https://www.x.org/wiki/) as a window server. Adittionally [systemd](https://en.wikipedia.org/wiki/Systemd) is desirable too, since the installation script will install a couple of services to start the app from your gamepad at any time, those services can be found under the [services](https://github.com/szz-dvl/GAL/tree/master/services) folder.

### Installing
For install this app please clone this repository:

```
git clone https://github.com/szz-dvl/GAL.git
cd GAL

```
And run the installation script:

```
./install.sh

```
This must suffice to start running the app. To uninstall the app please run the uninstallation script:

```
./uninstall.sh

```

### Configuring

For the application to be able to list your games you may configurate it a little bit. The configuration file, which must reside in the same directory of the source files must be named "confis.json", the file [config.skel](https://github.com/szz-dvl/GAL/blob/master/confis.skel) can be used as a skeleton to create one. This file contains examples to configure yours. However there are three main sections in this json:

#### Lists
Each object of this array will represent a list of games to be run with a particular emulator, here goes an example for Mupen64Plus:

```

		{
            "lid": "n64",
            "source": "/home/me/n64/",
			"ext": ".n64",
			"title": "n64 ROM files:",
			"class": "n64.N64_Emulator",
			"emu": {
				"panel": false,
				"name": "Mupen64Plus",
				"bin": "/usr/games/mupen64plus",
				"opt": ["--fullscreen", "--resolution", "1680x1050", "--osd", "--set", "Video-Rice[MultiSampling]=2"]
			},
			"extra": {
				"Super Mario 64": ["--set", "Video-Rice[MultiSampling]=1", "--gfx", "mupen64plus-video-rice"],
				"Smash": ["--set", "Video-Rice[MultiSampling]=1", "--gfx", "mupen64plus-video-glide64mk2"],
				"Majora's Mask": ["--set", "Video-Rice[MultiSampling]=1", "--gfx", "mupen64plus-video-glide64mk2"],
				"Bad Fur Day": ["--set", "Video-Rice[MultiSampling]=1", "--gfx", "mupen64plus-video-rice"],
				"Pokemon": ["--set", "Video-Rice[MultiSampling]=1", "--gfx", "mupen64plus-video-rice"],
				"Paper Mario": ["--set", "Video-Rice[MultiSampling]=1", "--gfx", "mupen64plus-video-glide64mk2"]
			}
		}
			
```

## Using the app

By default there will be button combinations to change the next slot to be loaded (usefull for emulators) binded to the left / right arrow keys ```lr_arrows``` and to increse and decrese the volume binded to the up / down arrows of the gamepad ```ud_arrows```. To trigger this functionalities the master button ```mtr_btn``` must be pressed. Additionally if one hold the four rear triggers (R1,R2,L1,L2) while master button is pressed the current session will be killed and the game lists will be again navigable.

Moreover, anyone willing to add some functionalities can easely implement extra button responses in a custom plugin, the file [emulator.skel](https://github.com/szz-dvl/GAL/blob/master/plugins/emulator.skel) may be used as a skeleton file to create it, those will need to reside under the plugins directory and passed in the "class" field of the config file. If no plugin is available for a given game or emulator no extra button functionalities will be mapped.

Have fun!


## Built With

* [Python](https://www.python.org/) - Python
* [Bash](https://angularjs.org/) - MVW
* [GitHub](https://github.com/) - Hosting

## Contributing

Mail me if you want to lend a hand.

## Authors

* **Szz** 

## License

This project is licensed under the Affero GPL license - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Any one using this project
