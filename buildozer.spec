[app]
title = Новая Жизнь
package.name = newlife
package.domain = com.denislife

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0

requirements = python3==3.11.6,kivy==2.3.1

orientation = portrait
fullscreen = 0

android.permissions =
android.api = 35
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

p4a.branch = develop

log_level = 2
warn_on_root = 1
