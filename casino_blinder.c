#include <furi.h>
#include <gui/gui.h>
#include <input/input.h>
#include <lib/subghz/subghz_tx_rx_worker.h>
#include <lib/subghz/devices/cc1101_int/cc1101_int_interconnect.h>
#include <lib/subghz/devices/devices.h>
#include <casino_blinder_icons.h>

#define NUM_FRAMES 100
#define ANIMATION_FPS 30

typedef enum {
    AppStateIdle,
    AppStateTransmitting,
} AppState;

typedef struct {
    Gui* gui;
    ViewPort* view_port;
    FuriMessageQueue* event_queue;
    FuriTimer* timer;
    AppState state;
    const SubGhzDevice* device;
    uint32_t transmit_start_time;
    bool signal_up;  // true = up arrow signal, false = down arrow signal
    uint8_t current_frame;  // 0-99
} CasinoBlinder;

// Icon array mapping frame number to icon
static const Icon* get_frame_icon(uint8_t frame_num) {
    const Icon* frames[NUM_FRAMES] = {
        &I_frame_000, &I_frame_001, &I_frame_002, &I_frame_003, &I_frame_004,
        &I_frame_005, &I_frame_006, &I_frame_007, &I_frame_008, &I_frame_009,
        &I_frame_010, &I_frame_011, &I_frame_012, &I_frame_013, &I_frame_014,
        &I_frame_015, &I_frame_016, &I_frame_017, &I_frame_018, &I_frame_019,
        &I_frame_020, &I_frame_021, &I_frame_022, &I_frame_023, &I_frame_024,
        &I_frame_025, &I_frame_026, &I_frame_027, &I_frame_028, &I_frame_029,
        &I_frame_030, &I_frame_031, &I_frame_032, &I_frame_033, &I_frame_034,
        &I_frame_035, &I_frame_036, &I_frame_037, &I_frame_038, &I_frame_039,
        &I_frame_040, &I_frame_041, &I_frame_042, &I_frame_043, &I_frame_044,
        &I_frame_045, &I_frame_046, &I_frame_047, &I_frame_048, &I_frame_049,
        &I_frame_050, &I_frame_051, &I_frame_052, &I_frame_053, &I_frame_054,
        &I_frame_055, &I_frame_056, &I_frame_057, &I_frame_058, &I_frame_059,
        &I_frame_060, &I_frame_061, &I_frame_062, &I_frame_063, &I_frame_064,
        &I_frame_065, &I_frame_066, &I_frame_067, &I_frame_068, &I_frame_069,
        &I_frame_070, &I_frame_071, &I_frame_072, &I_frame_073, &I_frame_074,
        &I_frame_075, &I_frame_076, &I_frame_077, &I_frame_078, &I_frame_079,
        &I_frame_080, &I_frame_081, &I_frame_082, &I_frame_083, &I_frame_084,
        &I_frame_085, &I_frame_086, &I_frame_087, &I_frame_088, &I_frame_089,
        &I_frame_090, &I_frame_091, &I_frame_092, &I_frame_093, &I_frame_094,
        &I_frame_095, &I_frame_096, &I_frame_097, &I_frame_098, &I_frame_099,
    };
    return frames[frame_num % NUM_FRAMES];
}

static void casino_blinder_draw_callback(Canvas* canvas, void* ctx) {
    CasinoBlinder* app = ctx;
    furi_assert(app);

    canvas_clear(canvas);

    if(app->state == AppStateTransmitting) {
        // Draw current animation frame
        const Icon* frame = get_frame_icon(app->current_frame);
        canvas_draw_icon(canvas, 0, 0, frame);
    } else {
        canvas_set_font(canvas, FontPrimary);
        canvas_draw_str_aligned(canvas, 64, 20, AlignCenter, AlignCenter, "Casino Blinder");
        canvas_set_font(canvas, FontSecondary);
        canvas_draw_str_aligned(canvas, 64, 35, AlignCenter, AlignCenter, "UP: Signal 1");
        canvas_draw_str_aligned(canvas, 64, 47, AlignCenter, AlignCenter, "DOWN: Signal 2");
        canvas_draw_str_aligned(canvas, 64, 59, AlignCenter, AlignCenter, "BACK: Exit");
    }
}

static void casino_blinder_input_callback(InputEvent* input_event, void* ctx) {
    furi_assert(ctx);
    FuriMessageQueue* event_queue = ctx;
    furi_message_queue_put(event_queue, input_event, FuriWaitForever);
}

static void timer_callback(void* ctx) {
    CasinoBlinder* app = ctx;
    furi_assert(app);

    if(app->state == AppStateTransmitting) {
        // Advance to next frame
        app->current_frame++;

        // Check if animation finished
        if(app->current_frame >= NUM_FRAMES) {
            app->current_frame = 0;
            app->state = AppStateIdle;
            furi_timer_stop(app->timer);
        }

        // Request redraw
        view_port_update(app->view_port);
    }
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
    app->current_frame = 0;

    // Initialize SubGHz devices
    subghz_devices_init();
    app->device = subghz_devices_get_by_name(SUBGHZ_DEVICE_CC1101_INT_NAME);

    // Create message queue for input events
    app->event_queue = furi_message_queue_alloc(8, sizeof(InputEvent));

    // Create timer for animation (33ms = ~30 FPS)
    app->timer = furi_timer_alloc(timer_callback, FuriTimerTypePeriodic, app);

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
        if(furi_message_queue_get(app->event_queue, &event, 100) == FuriStatusOk) {
            if(event.type == InputTypePress) {
                if(event.key == InputKeyBack) {
                    running = false;
                } else if(event.key == InputKeyUp && app->state == AppStateIdle) {
                    // Transmit signal 1 (UP) with animation
                    app->signal_up = true;
                    app->state = AppStateTransmitting;
                    app->current_frame = 0;
                    app->transmit_start_time = furi_get_tick();
                    transmit_signal(app, true);
                    furi_timer_start(app->timer, 1000 / ANIMATION_FPS);  // 33ms for 30 FPS
                    view_port_update(app->view_port);
                } else if(event.key == InputKeyDown && app->state == AppStateIdle) {
                    // Transmit signal 2 (DOWN) with animation
                    app->signal_up = false;
                    app->state = AppStateTransmitting;
                    app->current_frame = 0;
                    app->transmit_start_time = furi_get_tick();
                    transmit_signal(app, false);
                    furi_timer_start(app->timer, 1000 / ANIMATION_FPS);  // 33ms for 30 FPS
                    view_port_update(app->view_port);
                }
            }
        }
    }

    // Cleanup
    furi_timer_stop(app->timer);
    furi_timer_free(app->timer);
    subghz_devices_deinit();
    gui_remove_view_port(app->gui, app->view_port);
    view_port_free(app->view_port);
    furi_record_close(RECORD_GUI);
    furi_message_queue_free(app->event_queue);
    free(app);

    return 0;
}
