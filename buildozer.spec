[app]
title = SafeStep
package.name = safestep
package.domain = org.uncp
source.dir = .
source.include_exts = py,kv,pt,wav,md
source.include_patterns = assets/*.wav,models/*.pt
version = 1.0
requirements = python3,kivy==2.3.0,opencv-python==4.9.0.80,ultralytics==8.2.0,numpy,requests==2.32.5
orientation = portrait
fullscreen = 1

android.permissions = CAMERA,INTERNET
android.minapi = 24
