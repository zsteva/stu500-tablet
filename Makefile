
dep:
	apt-get install -y python3-uinput python3-evdev python3-hid

install: dep
	install -o 0 -g 0 -m 0755 stu500-tablet.py /usr/local/bin/
	install -o 0 -g 0 -m 0644 stu500-tablet.service /etc/systemd/system/
	install -o 0 -g 0 -m 0644 92-sig-stu500-tablet.rules /etc/udev/rules.d/

	systemctl daemon-reload

