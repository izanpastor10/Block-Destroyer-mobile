[app]
title = Block Destroyer
package.name = blockdestroyer
package.domain = org.izan
source.dir = .
source.include_exts = py,png,jpg,json,ttf,wav,ogg
version = 1.0

requirements = python3,pygame

orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 1
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
