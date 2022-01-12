# Conditional Dependencies

Some logic require dependencies only under specific cases.

Use lazy dependency declarations when you want to avoid resolution until it is
absolutely necessary:

``` python
from deadsimple import Lazy


class DoorUnlocker:
    def unlock(self, door):
        ...


def get_door_unlocker():
    return DoorUnlocker()


class DoorOpener:
    door_unlocker = Lazy(get_door_unlocker)

    def open_door(self, door):

        if door.is_locked:
            self.door_unlocker.lazy.unlock(door)

        door.turn_handle()
        door.push()
```

This way `get_door_unlocker` and `DoorUnlocker` are called and instantiated only
if `door.is_locked`.
