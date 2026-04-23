# RoboCup @Home - Home Education Robot

This repository contains the full ROS-based software stack used in our RoboCup @Home project.

## Competition Result

This is the project we used to join RoboCup @Home. Our team achieved:

- First place in Egypt
- Qualification to the RoboCup international stage

## Challenge Task We Solved

The run starts with map scanning and ends with a full guest report to the host.

1. Build/scan the map of the environment.
2. Place the robot anywhere in the host room.
3. Give the command: **"find my guest"**.
4. The robot navigates to the guest room.
5. The robot visits guests one by one and asks each person for their name.
6. The robot returns to the host.
7. For every detected guest, the robot reports:
   - The name
   - At least two features (for example: t-shirt color, pants color, hair, gender)
   - A nearby object (for example: chair, TV, table)
   - The relative location of that object with respect to the person
8. The vision system creates a bounding box around the detected nearby object.

## What The System Provides

- Mapping and map usage
- Localization and room-to-room navigation
- Speech understanding and speech synthesis
- Guest interaction (ask-and-collect names)
- Person feature extraction
- Nearby object detection and relation estimation
- Spoken summary generation for the host

## Repository Layout

- `rchomeedu_mapping/`: mapping visualization resources
- `rchomeedu_navigation/`: path planning, movement scripts, and maps
- `rchomeedu_speech/`: speech recognition and text-to-speech stack
- `rchomeedu_sr/`: additional speech/name scripts
- `rchomeedu_vision/`: perception pipeline, tracker logic, and Gemini integration
- `rchomeedu_arm/`: arm motion and gesture scripts

## Key Files And Their Roles

### rchomeedu_arm

- `launch/arm.launch`: launch configuration for arm subsystem
- `param/joints.yaml`: joint configuration values used by arm nodes
- `scripts/arm.py`: main arm control behavior
- `scripts/dance_arm.py`: expressive arm movement routine

### rchomeedu_mapping

- `mapping.rviz`: RViz setup used while mapping and validating map quality

### rchomeedu_navigation

- `launch/navigation.launch`: navigation stack entry point
- `maps/homeedu_montesilvano.yaml`: map metadata used by map server/localization
- `maps/homeedu_montesilvano.pgm`: occupancy map image
- `scripts/navigation.py`: navigation behavior implementation
- `scripts/navigation2.py`: point-to-point and helper navigation interface
- `scripts/move.py`: movement utility/control script
- `scripts/navitst.py`: navigation test script

### rchomeedu_speech

- `launch/lm.launch`: language model and recognition launch
- `launch/talkback.launch`: conversational loop launch
- `launch/sound_test.launch`: audio output/input test launch
- `robocup/robocup.corpus`: corpus used to build language resources
- `robocup/robocup.dic`: pronunciation dictionary
- `robocup/robocup.kwlist`: keyword list
- `robocup/robocup.lm`: language model
- `robocup/robocup.sent`: sentences source file
- `robocup/robocup.vocab`: vocabulary list
- `scripts/google_sr.py`: speech recognition integration
- `scripts/google_tts.py`: text-to-speech integration
- `scripts/chatbot.py`: dialogue/interaction helper
- `scripts/talkback.py`: interactive speech pipeline
- `scripts/lm_test.py`: language model testing utility
- `scripts/sound_test.py`: sound testing utility
- `scripts/tst.py`: quick speech test helper

### rchomeedu_sr

- `ask_name.py`: guest name acquisition flow
- `ask_name_2.py`: alternate guest name flow
- `tts.py`: text-to-speech helper script

### rchomeedu_vision

- `launch/multi_astra.launch`: multi-camera/perception launch
- `scripts/main_tracker.py`: main orchestration for detection and tracking
- `scripts/camera_to_gemini.py`: camera frame to Gemini analysis bridge
- `scripts/gemini_analyzer.py`: high-level Gemini response processing
- `scripts/gemini_functions.py`: Gemini-related helper functions
- `scripts/states_logic.py`: state machine logic for behavior transitions
- `scripts/callbacks.py`: ROS callback handlers
- `scripts/shared_state.py`: shared runtime state container
- `scripts/config.py`: runtime configuration constants
- `scripts/utils.py`: utility helpers
- `scripts/person 1/features.txt`: saved features for person profile 1
- `scripts/person 2/features.txt`: saved features for person profile 2
- `scripts/person 3/features.txt`: saved features for person profile 3
- `person_frame_raw.jpg`: captured raw person frame example
- `person_frame_annotated.jpg`: annotated frame example with visual overlays

## Typical Runtime Sequence

1. Launch robot base and sensors.
2. Prepare mapping/localization and load map.
3. Launch navigation, speech, and vision packages.
4. Wait for host command: **"find my guest"**.
5. Navigate to guests, collect names/features/nearby objects.
6. Return to host and deliver spoken report per guest.

## Main Entry Points

- `rchomeedu_arm/launch/arm.launch`
- `rchomeedu_navigation/launch/navigation.launch`
- `rchomeedu_speech/launch/lm.launch`
- `rchomeedu_speech/launch/talkback.launch`
- `rchomeedu_vision/launch/multi_astra.launch`

## Notes

- Calibrate sensors, topics, and frame IDs for your robot before live runs.
- Tune navigation and perception thresholds per environment.

## License

Add your preferred license information here.

## Competition Photo

![Egypt Champions](Egypt%20Champions.jpeg)
