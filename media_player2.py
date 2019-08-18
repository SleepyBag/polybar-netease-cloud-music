#!/usr/bin/env python3
import sys
try:
    # http://click.pocoo.org/5/why/
    import click
    import dbus
    from colored import fg, stylize
except:
    print("Need to install click, dbus-python and colored")
    sys.exit(-1)


class Player:

    _name = None
    _service = None
    _player = None
    _interface = None
    _bus = dbus.SessionBus()
    _info = {}
    _pause_icon = "\uf04c"
    _play_icon = "\uf04b"
    _trackMap = {
        'trackid': 'mpris:trackid',
        'length': 'mpris:length',
        'artUrl': 'mpris:artUrl',
        'album': 'xesam:album',
        'artist': 'xesam:artist',
        'title': 'xesam:title',
        'url': 'xesam:url',
        'rating': 'xesam:autoRating',
        'status': 'PlaybackStatus',
    }

    def __init__(self, service):
        self._service = service
        self._name = service.split('.')[-1]
        self._player = self._bus.get_object(self._service,
                                            '/org/mpris/MediaPlayer2')
        self._interface = dbus.Interface(
            self._player, dbus_interface='org.freedesktop.DBus.Properties')
        self.get_metadata()

    # Get all availables information from DBus for a player object
    def get_metadata(self):
        self._info = {}
        metadata = self._interface.GetAll('org.mpris.MediaPlayer2.Player')
        for key, val in metadata.items():
            if isinstance(val, dict):
                for subk, subv in val.items():
                    self._info[subk] = subv
            self._info[key] = val

    def is_playing(self):
        return self._info['PlaybackStatus'] == 'Playing'

    # Print information for a player
    def print_metadata(self):
        for k, v in self._trackMap.items():
            if v not in self._info:
                continue
            val = self._info[v]
            print("{}: {}".format(
                stylize(k, fg('red')),
                stylize(', '.join(val) if isinstance(val, list) else val,
                        fg('blue'))))

    def next(self):
        dbus.Interface(
            self._player,
            dbus_interface='org.mpris.MediaPlayer2.Player').Next()

    def prev(self):
        dbus.Interface(
            self._player,
            dbus_interface='org.mpris.MediaPlayer2.Player').Previous()

    def play_pause(self):
        dbus.Interface(
            self._player,
            dbus_interface='org.mpris.MediaPlayer2.Player').PlayPause()

    def stop(self):
        dbus.Interface(
            self._player,
            dbus_interface='org.mpris.MediaPlayer2.Player').Stop()

    def get_value(self, key):
        try:
            value = self._info[key]
            if isinstance(value, int):
                import datetime
                return str(datetime.timedelta(microseconds=value))

            return ''.join(self._info[key])
        except KeyError:
            return ''

    def print_to_bar(self, spacing, icolor=None, tcolor=None):
        text = None
        icon = "{}".format(self._play_icon
                           if self.is_playing() else self._pause_icon)
        if not (icolor is None):
            icon = stylize(icon, fg(icolor))

        text = "{} - {}".format(
            self.get_value(self._trackMap['title']),
            self.get_value(self._trackMap['artist']))
        if text is None:
            text = "{} - {}".format(
                self.get_value(self._trackMap['status']),
                self.get_value(self._trackMap['length']))
        if not (tcolor is None):
            text = stylize(text, fg(tcolor))
        print(icon + spacing * " " + text)


players = {}


def get_services(name):
    global players

    def test(s):
        return name in s or 'org.mpris.MediaPlayer2' in s

    try:
        players = {
            str(s.split('.')[-1]): Player(s)
            for s in dbus.SessionBus().list_names() if test(s)
        }
    except:
        pass


@click.group()
def cmd():
    pass


@cmd.command()
@click.argument('pref_player')
@click.option('--colors', nargs=2)
@click.option('--spacing', nargs=1, type=int, default=1)
def print_info(pref_player, colors=None, spacing=None):
    try:
        icolor = colors[0]
        tcolor = colors[1]
    except (KeyError, IndexError):
        icolor = None
        tcolor = None
    get_services(pref_player)
    if pref_player in players.keys():
        players[pref_player].print_to_bar(spacing, icolor, tcolor)
    else:
        [s.print_to_bar(spacing, icolor, tcolor) for s in players.values()]


@cmd.command()
@click.argument('pref_player')
def next(pref_player):
    get_services(pref_player)
    if pref_player in players.keys():
        players[pref_player].next()
    else:
        [p.next() for p in players.values() if p.is_playing()]


@cmd.command()
@click.argument('pref_player')
def prev(pref_player):
    get_services(pref_player)
    if pref_player in players.keys():
        players[pref_player].prev()
    else:
        [p.prev() for p in players.values() if p.is_playing()]


@cmd.command()
@click.argument('pref_player')
def play_pause(pref_player):
    get_services(pref_player)
    if pref_player in players.keys():
        players[pref_player].play_pause()
    else:
        [p.play_pause() for p in players.values()]


@cmd.command()
@click.argument('pref_player')
def stop(pref_player):
    get_services(pref_player)
    if pref_player in players.keys():
        players[pref_player].stop()
    else:
        [p.stop() for p in players.values() if p.is_playing()]


_trackMap = {
    'trackid': 'mpris:trackid',
    'length': 'mpris:length',
    'artUrl': 'mpris:artUrl',
    'album': 'xesam:album',
    'artist': 'xesam:artist',
    'title': 'xesam:title',
    'url': 'xesam:url',
    'rating': 'xesam:autoRating',
    'status': 'PlaybackStatus',
}


def print_me(name, data, other):
    text = None
    _play_icon = "\uf04b"
    icon = "{}".format(_play_icon)
    text = "{} - {}".format(
        data['Metadata'].get(_trackMap['title']),
        ', '.join(data['Metadata'].get(_trackMap['artist'])))
    print(icon + " " + text)
    sys.exit(1)


if __name__ == '__main__':
    cmd()
