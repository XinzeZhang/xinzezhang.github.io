---

title:      Reset Bluetooth on mac
tags:
    -mac
    -bluetooth
---

## Reset the Bluetooth cache

Firstly, close the bluetooth of the Mac.
```
sudo mv /Library/Preferences/com.apple.Bluetooth.plist /Library/Preferences/com.apple.Bluetooth.plist.bak
sudo sudo rm ~/Library/Preferences/ByHost/com.apple.Bluetooth.*.plist
```

Then restart the Mac.