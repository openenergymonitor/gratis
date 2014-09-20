# Using arch Linux

**This need to be re-checked**

This was only briefly tested on the Beaglebone Black.  This ought to
work with Arch on Raspberry Pi (**untested**).


# Initial SD Card creation

The Arch Linux has documented way to set this up:

For Beaglebone Black:

http://archlinuxarm.org/platforms/armv7/ti/beaglebone-black

For Raspberry Pi:

http://archlinuxarm.org/platforms/armv6/raspberry-pi


# Installing packages

Basic use of pacman can be found at:

https://wiki.archlinux.org/index.php/pacman

start by upgrading the existing packages and then reboot to ensure
system is consistent and latest kernel is running.

~~~~~
pacman -Syu
reboot
~~~~~

After start-up login as root again Install whatever utilites, editor,
shells you would normally use:

~~~~~
pacman -S mg zsh curl rsync
~~~~~

Install git, development and fuse libraries:

~~~~~
pacman -S git base-devel libfuse
~~~~~


# Create a user to use for EPD development

Create a user for development, I like to set its shell to zsh.

~~~~~
# EITHER use the default shell (likely to be bash)
adduser -c 'E-Ink devlopment' -G root,wheel,adm -m -U repaper
# OR to use zsh as the user shell
adduser -c 'E-Ink devlopment' -G root,wheel,adm -m -U -s /usr/bin/zsh repaper
~~~~~

You may wish to change `root` and `repaper` passwords at this point.

~~~~~
passwd root
passwd repaper
~~~~~

Perhaps even set up ssh authorisation:

~~~~~
su -l repaper    # login as repaper
mkdir -m 0700 .ssh
cat > .ssh/authorized_keys
~~~~~

Now paste the correct public key into the terminal, press `Enter` and
then press `Ctrl-D`.  Press `Ctrl-D` to logout from `repaper` and try
ssh as repaper in another console on the host machine.

**Optional step:**

Now use `scp` to copy any shell or editor configuration files from the host
(I copy my zsh and mg settings)

~~~~~
#* this is on the host machine and I have the DCHP server provide DNS for Beaglebone Black
scp -p ~/.zshrc ~/.mg repaper@beaglebone:
#* it maybe necessary to use IP address (replace with your correct IP address)
scp -p ~/.zshrc ~/.mg repaper@192.168.1.123:
~~~~~

# Creating the EPD driver

Login as the newly created `repaper` user and clone the repaper repository:

~~~~~
git clone https://github.com/repaper/gratis.git
~~~~~

## Special GPIO section for Beaglebone Black

This is to install the cape manager firmware files that allow the
Beaglebone Black version of Arch Linux to have access to the GPIO.

Clone the nomel repository from https://github.com/nomel/beaglebone
then install the necessary P9 firmware files:

~~~~~
git clone https://github.com/nomel/beaglebone.git
sudo cp beaglebone/gpio-header/generated/gpio-P9.* /lib/firmware
~~~~~

Optional step:

If you intend to make changes to use the P8 GPIO pin header then also
add the P8 firmware files as follows:

~~~~~
sudo cp beaglebone/gpio-header/generated/gpio-P8.* /lib/firmware
~~~~~


## Compiling and running

Install the necessary libraries and compile

~~~~~
cd gratis/PlatformWithOS
make help   # follow the various make options
# e.g.
make COG_VERSION=V2 bb-clean bb
# run the test program (in this case a 2.7" panel was connected)
sudo ./driver-common/epd_test 2.7
# the panel should cycle through several images
#
# install the epd driver
sudo make COG_VERSION=V2 bb-install
# Remember to edit the configuration (and set the correct panel size)
sudo mg /etc/default/epd-fuse
# start the driver
sudo service epd-fuse start
# run demo
python demo/DrawDemo.py
~~~~~

Note that once the demo has run successfully, please reboot, login and
check the fuse driver was loaded:

~~~~~
cat /dev/epd/panel
# this should display panel size and COG version
#
# try clearing the panel (all white)
echo 'C' > /dev/epd/command
~~~~~

Any of the demos should now be runnable.