# Casino Blinder

A Flipper Zero app for SubGHz signal playback with custom sliding animations.

## Features

- Two hardcoded SubGHz signals
- Up arrow: Play signal #1 with bottom-to-center sliding animation
- Down arrow: Play signal #2 with top-to-center sliding animation
- 15-second animation display on signal transmission

## Installation

1. Copy the compiled `.fap` file to your Flipper Zero's `apps` folder on the SD card
2. Navigate to Applications > GPIO on your Flipper Zero
3. Launch "Casino Blinder"

## Building

This app requires the Flipper Zero development environment (`ufbt`):

```bash
ufbt
```

The compiled `.fap` file will be in the `dist` folder.

## Usage

- Press **Up arrow** to transmit signal #1
- Press **Down arrow** to transmit signal #2
- Each transmission triggers a 15-second animation
- Press **Back** to exit the app

## Development Status

- [x] Hello World boilerplate
- [ ] SubGHz signal playback
- [ ] Basic animations
- [ ] Custom sliding animations
