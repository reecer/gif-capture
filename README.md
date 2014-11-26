gif-capture
===========

Byzanz interface to easily capture animated GIFs of your screen.

Requirements
============
###Byzanz
```
sudo add-apt-repository ppa:fossfreedom/byzanz
sudo apt-get update
sudo apt-get install byzanz
```

Installation
============
Currently, it is easiest to clone this repo and symlink `gif-capture.py`

###Cloning
```git clone http://github.com/reecer/gif-capture```
###Symlinking
```
cd gif-capture
ln `pwd`/gif-capture.py ~/bin/gif-cap
```


Config
========
* `ESC` will **quit**.
* **Saves** to `~/Pictures`
* By default, the gif is a 10 second lapse. This `DURATION` can be changed by editing the variable on *line 10*.
