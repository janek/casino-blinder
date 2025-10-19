# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Python Usage

**ALWAYS use `uv` instead of `python3` or `python` directly.**

Examples:
```bash
uv run script.py          # Run scripts
uv pip install package    # Install packages
```

## Build Commands

### Primary Commands (via Makefile)
```bash
make build          # Build the .fap file
make launch         # Build and launch on connected Flipper
make clean          # Clean build artifacts
make list-subghz    # List SubGHz files on Flipper SD card
```

### Direct ufbt Commands
```bash
ufbt                # Build the app (creates dist/casino_blinder.fap)
ufbt launch         # Build and launch on Flipper
ufbt clean          # Clean build artifacts
```

## Architecture Overview

### Event-Driven ViewPort Application

This is a **simple ViewPort-based app** (not SceneManager/ViewDispatcher). The architecture:

- **Main Loop**: Polls `FuriMessageQueue` for input events (100ms timeout)
- **State Machine**: `AppStateIdle` ↔ `AppStateTransmitting` (15-second timer)
- **Drawing**: `casino_blinder_draw_callback()` renders UI based on current state
- **Input**: `casino_blinder_input_callback()` queues button presses

### SubGHz Signal Workflow

The app uses **hardcoded RAW signals** (not protocol-based encoding):

1. Raw .sub files stored in `signals/` (Cas_d_1_trimmed.sub, Cas_d_2_trimmed.sub)
2. Converted to C arrays via `tools/sub_to_c_array.py` → `signals/signals.h`
3. Signal data: 433.92 MHz, OOK modulation, timing arrays (positive=ON, negative=OFF in μs)
4. **Current status**: `transmit_signal()` is a placeholder (actual transmission not yet implemented)

### Signal Processing Tools (tools/)

- **sub_to_wav.py**: Convert .sub RAW → WAV for Audacity visualization
- **trim_sub.py**: Trim .sub files by microsecond timestamps (lossless)
- **sub_to_c_array.py**: Generate C header files with signal arrays

**Workflow**: Record signal on Flipper → Transfer .sub file → Visualize with sub_to_wav.py → Identify timestamps in Audacity → Trim with trim_sub.py → Convert to C array with sub_to_c_array.py

### Animation Implementation (Pending)

Target: 100-frame sliding animation triggered on signal transmission.

**Requirements**:
- Flipper display: 128×64 pixels, 1-bit monochrome
- Images must be pre-converted to 1-bit before placing in `images/`
- ufbt auto-compiles PNGs → `casino_blinder_icons.h` (prefix: `I_`)
- Use `furi_timer_alloc()` with 33ms period for ~30 FPS
- Draw with `canvas_draw_icon(canvas, x, y, I_iconname)`

**Image conversion**: Use Floyd-Steinberg dithering for best monochrome results.

### File Organization

```
signals/           # SubGHz RAW files (.sub) and generated signals.h
tools/             # Python scripts for signal processing
images/            # PNG assets (auto-compiled by ufbt)
casino_blinder.c   # Main application entry point
application.fam    # App manifest (appid, version, category, etc.)
```

## Key Implementation Details

### FURI/Flipper-Specific Patterns

- **Never block the main thread**: No `furi_delay_ms()` in event loop (causes watchdog timeout)
- **Use FuriTimer for animations**: Allocate with `furi_timer_alloc(callback, FuriTimerTypePeriodic, context)`
- **Memory management**: All FURI objects must be freed in reverse allocation order
- **Thread-safe updates**: Call `view_port_update()` to trigger redraw from timer callbacks

### SubGHz Device Initialization

```c
subghz_devices_init();
app->device = subghz_devices_get_by_name(SUBGHZ_DEVICE_CC1101_INT_NAME);
// ... use device ...
subghz_devices_deinit();  // Always cleanup
```

### Current Development Status

- ✅ Hello World boilerplate with ViewPort
- ✅ SubGHz device initialization
- ✅ 15-second transmission timer
- ✅ Signal data prepared in signals.h
- ⏳ Actual SubGHz transmission (placeholder only)
- ⏳ Animation implementation (research completed, pending implementation)
