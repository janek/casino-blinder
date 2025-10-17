.PHONY: build clean launch install list-subghz help

# Flipper device port (auto-detected)
FLIPPER_PORT ?= /dev/tty.usbmodemflip_Akerir1

help:
	@echo "Casino Blinder - Flipper Zero Build Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build        - Build the app"
	@echo "  clean        - Clean build artifacts"
	@echo "  launch       - Build and launch on Flipper"
	@echo "  install      - Build and install (without launching)"
	@echo "  list-subghz  - List SubGHz files on Flipper SD card"
	@echo "  help         - Show this help message"

build:
	@echo "🔨 Building Casino Blinder..."
	ufbt

clean:
	@echo "🧹 Cleaning build artifacts..."
	ufbt clean

launch: build
	@echo "🚀 Launching on Flipper..."
	ufbt launch FLIPPER=$(FLIPPER_PORT)

install: build
	@echo "📦 Installing to Flipper..."
	python3 ~/.ufbt/current/scripts/runfap.py -p $(FLIPPER_PORT) -s ~/.ufbt/build/casino_blinder.fap -t /ext/apps/GPIO/casino_blinder.fap

list-subghz:
	@echo "📁 Listing SubGHz files on Flipper..."
	@ufbt cli --port $(FLIPPER_PORT) --exec "storage list /ext/subghz" 2>&1 | grep -E '\.sub$$' || echo "❌ No .sub files found or Flipper not connected"
