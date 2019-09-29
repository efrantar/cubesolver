mirrcub3r
=========

This repository contains the full source-code of *mirrcub3r*, a Lego Mindstorms robot that solves a random Rubik's Cube in 1.5 seconds on average. As of September 5th 2019 it is the fastest Lego-based cube-solver in the world.

A video showcasing the solver can be found here: TODO

The robot is built from two Lego Mindstorms EV3s, 8 Medium Motors, many (red) Lego bricks, a (slightly modified) GAN 356R cube and 4 small mirrors (hence also the >>mirr<< in its name). The latter allow the robot to see all 6 sides of the cube at once using only a single camera and thus enabling ~5ms scan times (due to the robot not being able to rotate the entire cube this would otherwise take several seconds). For that purpose a smart-phone running the app [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam&hl=en_GB) is used. The whole process is controlled by a Python application running on a PC which communicates with the robot via Direct Commands (to leverage the best optimized motor drivers directly from Lego and to minimize any additional overhead caused by alternative VMs) using Christoph Gaukel's excellent [ev3-python3](https://github.com/ChristophGaukel/ev3-python3) API. Solutions are computed by the [rob-twophase](https://github.com/efrantar/twophase) solver running on an AMD Ryzen 3600 processor with 6 cores / 12 threads in `-DFACES5 -DAXIAL -DQUARTER` mode which has the robot mechanics (both its restrictions but also its special capabilites) deeply built in and thereby finds ~20% faster to execute solutions within milliseconds.

*Note that the code provided here is primarily intended for people interested in the underlying techniques of an extremely fast cube-solver. If you just want built a robot from instructions and run it with fully prewritten software, this is not the right place to look. Furthermore, while version 1.0 of mirrcub3r is now finally complete, I will still be actively working on improving it and thus the contents of this repository are subject to change.*

Sample solves (will be removed once the official video is released): [1.400](https://youtu.be/E7asXTJ8pAY) (decent, not too lucky), [1.686](https://youtu.be/pTgFNbZgjuA) (fairly unlucky), [0.972](https://youtu.be/JhygBTWfFqc) (ultra lucky)
