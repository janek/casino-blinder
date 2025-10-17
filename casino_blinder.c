#include <furi.h>
#include <gui/gui.h>
#include <input/input.h>
#include <lib/subghz/subghz_tx_rx_worker.h>
#include <lib/subghz/devices/cc1101_int/cc1101_int_interconnect.h>
#include <lib/subghz/devices/devices.h>

typedef enum {
    AppStateIdle,
    AppStateTransmitting,
} AppState;

typedef struct {
    Gui* gui;
    ViewPort* view_port;
    FuriMessageQueue* event_queue;
    AppState state;
    const SubGhzDevice* device;
    uint32_t transmit_start_time;
    bool signal_up;  // true = up arrow signal, false = down arrow signal
} CasinoBlinder;

static void casino_blinder_draw_callback(Canvas* canvas, void* ctx) {
    CasinoBlinder* app = ctx;
    furi_assert(app);

    canvas_clear(canvas);
    canvas_set_font(canvas, FontPrimary);
    canvas_draw_str_aligned(canvas, 64, 10, AlignCenter, AlignCenter, "Casino Blinder");

    canvas_set_font(canvas, FontSecondary);

    if(app->state == AppStateTransmitting) {
        uint32_t elapsed = (furi_get_tick() - app->transmit_start_time) / 1000;
        uint32_t remaining = 15 - elapsed;

        char status[32];
        snprintf(status, sizeof(status), "Transmitting %s...", app->signal_up ? "UP" : "DOWN");
        canvas_draw_str_aligned(canvas, 64, 25, AlignCenter, AlignCenter, status);

        char time[32];
        snprintf(time, sizeof(time), "Time: %lu sec", remaining);
        canvas_draw_str_aligned(canvas, 64, 40, AlignCenter, AlignCenter, time);
    } else {
        canvas_draw_str_aligned(canvas, 64, 30, AlignCenter, AlignCenter, "UP: Signal 1");
        canvas_draw_str_aligned(canvas, 64, 42, AlignCenter, AlignCenter, "DOWN: Signal 2");
        canvas_draw_str_aligned(canvas, 64, 54, AlignCenter, AlignCenter, "BACK: Exit");
    }
}

static void casino_blinder_input_callback(InputEvent* input_event, void* ctx) {
    furi_assert(ctx);
    FuriMessageQueue* event_queue = ctx;
    furi_message_queue_put(event_queue, input_event, FuriWaitForever);
}

// TODO(human): Configure your SubGHz signal parameters here
// Signal 1 (UP arrow): Modify frequency, protocol, and data
// Signal 2 (DOWN arrow): Modify frequency, protocol, and data
//
// Example frequencies:
//   433920000 (433.92 MHz) - Common for garage doors, remote switches
//   315000000 (315 MHz)    - Common in North America
//   868350000 (868.35 MHz) - Common in Europe
//
// You'll need to:
//   1. Set the frequency for each signal
//   2. Choose a protocol (Princeton, Came, etc.) or use raw data
//   3. Provide the actual signal data you want to transmit
//
// WARNING: Only transmit on frequencies legal in your region!

static void transmit_signal(CasinoBlinder* app, bool is_up_signal) {
    UNUSED(app);
    UNUSED(is_up_signal);

    // TODO(human): Implement actual SubGHz transmission here
    //
    // For now, this is a placeholder that just shows the UI animation.
    // To actually transmit signals, you'll need to:
    //
    // 1. Initialize the SubGHz device:
    //    subghz_devices_reset(app->device);
    //    subghz_devices_idle(app->device);
    //
    // 2. Configure frequency and modulation:
    //    uint32_t frequency = is_up_signal ? 433920000 : 315000000;
    //    subghz_devices_load_preset(app->device, FuriHalSubGhzPresetOok650Async, NULL);
    //    frequency = subghz_devices_set_frequency(app->device, frequency);
    //
    // 3. Set up protocol encoder with your signal data:
    //    - Use SubGhzProtocolEncoderPrinceton (or other protocol)
    //    - Or use raw signal data
    //
    // 4. Start async transmission with proper callback:
    //    subghz_devices_start_async_tx(app->device, callback_func, context);
    //
    // 5. Clean up after transmission completes:
    //    subghz_devices_stop_async_tx(app->device);
    //    subghz_devices_idle(app->device);
    //    subghz_devices_sleep(app->device);
    //
    // WARNING: Don't call blocking functions (furi_delay_ms) from the main thread!
}

int32_t casino_blinder_app(void* p) {
    UNUSED(p);

    CasinoBlinder* app = malloc(sizeof(CasinoBlinder));
    app->state = AppStateIdle;
    app->transmit_start_time = 0;
    app->signal_up = true;

    // Initialize SubGHz devices
    subghz_devices_init();
    app->device = subghz_devices_get_by_name(SUBGHZ_DEVICE_CC1101_INT_NAME);

    // Create message queue for input events
    app->event_queue = furi_message_queue_alloc(8, sizeof(InputEvent));

    // Set up GUI
    app->gui = furi_record_open(RECORD_GUI);
    app->view_port = view_port_alloc();

    view_port_draw_callback_set(app->view_port, casino_blinder_draw_callback, app);
    view_port_input_callback_set(app->view_port, casino_blinder_input_callback, app->event_queue);

    gui_add_view_port(app->gui, app->view_port, GuiLayerFullscreen);

    // Main event loop
    InputEvent event;
    bool running = true;

    while(running) {
        // Check if transmission timer expired
        if(app->state == AppStateTransmitting) {
            uint32_t elapsed = (furi_get_tick() - app->transmit_start_time) / 1000;
            if(elapsed >= 15) {
                app->state = AppStateIdle;
            }
            view_port_update(app->view_port);
        }

        if(furi_message_queue_get(app->event_queue, &event, 100) == FuriStatusOk) {
            if(event.type == InputTypePress) {
                if(event.key == InputKeyBack) {
                    running = false;
                } else if(event.key == InputKeyUp && app->state == AppStateIdle) {
                    // Transmit signal 1 (UP)
                    app->signal_up = true;
                    app->state = AppStateTransmitting;
                    app->transmit_start_time = furi_get_tick();
                    transmit_signal(app, true);
                    view_port_update(app->view_port);
                } else if(event.key == InputKeyDown && app->state == AppStateIdle) {
                    // Transmit signal 2 (DOWN)
                    app->signal_up = false;
                    app->state = AppStateTransmitting;
                    app->transmit_start_time = furi_get_tick();
                    transmit_signal(app, false);
                    view_port_update(app->view_port);
                }
            }
        }
    }

    // Cleanup
    subghz_devices_deinit();
    gui_remove_view_port(app->gui, app->view_port);
    view_port_free(app->view_port);
    furi_record_close(RECORD_GUI);
    furi_message_queue_free(app->event_queue);
    free(app);

    return 0;
}
