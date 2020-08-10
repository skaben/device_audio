# smart_tester

smart tester

alsa permission ("cannot find card '0'") fixes:

usermod -a -G audio <username>

or

setfacl -m u:<username>:rw /dev/snd/*

