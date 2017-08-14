# xiaomi wifi plug

Initial integration of Xiaomi wifi plug.

Thanks to [Rytilahti](https://github.com/rytilahti/python-mirobo) for all the work.

# Setup

```
switch:
  - platform: xiaomiplug
    name: Original Xiaomi Mi Smart WiFi Socket
    host: 192.168.130.59
    token: b7c4a758c251955d2c24b1d9e41ce47d
  - platform: xiaomiplug
    name: Xiaomi Mi Smart WiFi Socket 2
    host: 192.168.130.60
    token: 0ed0fdccb2d0cd718108f18a447726a6
```

# Features
* Basic functionality: on, off & current state
