# polybar-netease-cloud-music
Polybar module for netease-cloud-music

# Dependencies
* zsh (located at /bin/zsh, or you will need to modify the path of zsh in the scripts)
* inotifywait
* python-dbus
* python-gobject

# Installation
Put all of these files into a standalone directory. And then write into polybar config:
```
[module/previous]
type = custom/script
interval = 86400
format = "%{T3}<label>"
format-padding = 2
exec = echo ""
line-size = 1
click-left = "dbus-send --print-reply --dest=org.mpris.MediaPlayer2.netease-cloud-music /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Previous"

[module/next]
type = custom/script
interval = 86400
format = "%{T3}<label>"
format-padding = 2
exec = echo ""
line-size = 1
click-left = "dbus-send --print-reply --dest=org.mpris.MediaPlayer2.netease-cloud-music /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Next"

[module/playpause]
type = custom/script
format-padding = 2
exec = /path/to/polybar-netease-cloud-music/button_monitor
click-left = "dbus-send --print-reply --dest=org.mpris.MediaPlayer2.netease-cloud-music /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause"
tail = true

[module/netease]
type = custom/script
exec = /path/to/polybar-netease-cloud-music/monitor
tail = true
format-padding = 3
line-size = 1
click-left = i3-msg '[class="netease-cloud-music"] focus'
```

# usage
Initially, run **netease_listener.py** at background, which monitors the status of the player. Then add the module into your bar and you are easy to go.
