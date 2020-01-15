import time
import sys
import dbus
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    '-t',
    '--trunclen',
    type=int,
    metavar='trunclen'
)
parser.add_argument(
    '-f',
    '--format',
    type=str,
    metavar='custom format',
    dest='custom_format'
)
args = parser.parse_args()

# Default parameters
output = '{artist} : {song}'
trunclen = 15

# parameters can be overwritten by args
if args.trunclen is not None:
    trunclen = args.trunclen
if args.custom_format is not None:
    output = args.custom_format

try:
    session_bus = dbus.SessionBus()
    cloud_music_bus = session_bus.get_object(
        'org.mpris.MediaPlayer2.netease-cloud-music',
        '/org/mpris/MediaPlayer2'
    )

    cloud_music_properties = dbus.Interface(
        cloud_music_bus,
        'org.freedesktop.DBus.Properties'
    )

    metadata = cloud_music_properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')

    playback_status = str(cloud_music_properties.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus'))
    if 'mpris:length' in metadata:
        length = float(metadata['mpris:length'])
        position = float(cloud_music_properties.Get('org.mpris.MediaPlayer2.Player', 'Position'))
    else:
        length = 1.
        position = 0.
    percent = position / length

    artist = metadata['xesam:artist'][0]
    if len(artist) > trunclen:
        artist = artist[0:trunclen]
        artist += '...' 
        if ('(' in artist) and (')' not in artist):
            artist += ')'
    
    song = metadata['xesam:title']

    if len(song) > trunclen:
        song = song[0:trunclen]
        song += '...' 
        if ('(' in song) and (')' not in song):
            song += ')'

    if sys.version_info.major == 3:
        output = output.format(artist=artist, song=song)
    else:
        output = output.format(artist=artist, song=song).encode('UTF-8')
    percent = int((len(output) + 1) * percent)
    output = '%{o#EA2202}%{+o}' + output[: percent] + '%{-o}' + output[percent:]
    output = '%{F#EA2202} %{F-}' + output
    output += '  '

    output += '%{A1:dbus-send --print-reply --dest=org.mpris.MediaPlayer2.netease-cloud-music /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Previous:}    %{A}'
    if playback_status == 'Playing':
        output += '%{A1:dbus-send --print-reply --dest=org.mpris.MediaPlayer2.netease-cloud-music /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause:}    %{A}'
    else:
        output += '%{A1:dbus-send --print-reply --dest=org.mpris.MediaPlayer2.netease-cloud-music /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause:}    %{A}'
    output += '%{A1:dbus-send --print-reply --dest=org.mpris.MediaPlayer2.netease-cloud-music /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Next:}    %{A}'
    print(output)
    #  print('%{o#EA2202}%{+o}%{F#EA2202} %{F-}' + output + '%{o-}')

except Exception as e:
    if isinstance(e, dbus.exceptions.DBusException):
        print('%{A1:i3-msg workspace number 7 Netease; netease-cloud-music:}%{F#EA2202} %{F-}打开网易云音乐 %{A}')
    else:
        print(e)

