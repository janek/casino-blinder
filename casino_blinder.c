#include <furi.h>
#include <gui/gui.h>
#include <input/input.h>

typedef struct {
    Gui* gui;
    ViewPort* view_port;
    FuriMessageQueue* event_queue;
} CasinoBlinder;

static void casino_blinder_draw_callback(Canvas* canvas, void* ctx) {
    UNUSED(ctx);

    canvas_clear(canvas);
    canvas_set_font(canvas, FontPrimary);
    canvas_draw_str_aligned(canvas, 64, 20, AlignCenter, AlignCenter, "Casino Blinder");

    canvas_set_font(canvas, FontSecondary);
    canvas_draw_str_aligned(canvas, 64, 35, AlignCenter, AlignCenter, "Hello World!");
    canvas_draw_str_aligned(canvas, 64, 50, AlignCenter, AlignCenter, "Press Back to Exit");
}

static void casino_blinder_input_callback(InputEvent* input_event, void* ctx) {
    furi_assert(ctx);
    FuriMessageQueue* event_queue = ctx;
    furi_message_queue_put(event_queue, input_event, FuriWaitForever);
}

int32_t casino_blinder_app(void* p) {
    UNUSED(p);

    CasinoBlinder* app = malloc(sizeof(CasinoBlinder));

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
        if(furi_message_queue_get(app->event_queue, &event, 100) == FuriStatusOk) {
            if(event.type == InputTypePress || event.type == InputTypeRepeat) {
                if(event.key == InputKeyBack) {
                    running = false;
                }
            }
        }
    }

    // Cleanup
    gui_remove_view_port(app->gui, app->view_port);
    view_port_free(app->view_port);
    furi_record_close(RECORD_GUI);
    furi_message_queue_free(app->event_queue);
    free(app);

    return 0;
}
