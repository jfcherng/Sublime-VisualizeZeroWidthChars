import sublime
from .functions import (
    erase_phantom_set,
    is_view_normal_ready,
    is_view_too_large,
    is_view_typing,
    update_phantom_set,
    view_is_dirty_val,
)
from .Globals import global_get
from .log import log
from .RepeatingTimer import RepeatingTimer
from .utils import view_find_all_fast


class RendererThread(RepeatingTimer):
    def __init__(self, interval_ms: int = 1000) -> None:
        super().__init__(interval_ms, self._check_current_view)

        # to prevent from overlapped processes when using a low interval
        self.is_job_running = False

    def _check_current_view(self) -> None:
        if self.is_job_running:
            return

        self.is_job_running = True

        view = sublime.active_window().active_view()

        if is_view_normal_ready(view) and is_view_too_large(view):
            erase_phantom_set(view)
            view_is_dirty_val(view, False)

        if self._need_detect_chars_globally(view):
            self._detect_chars_globally(view)
            view_is_dirty_val(view, False)

        self.is_job_running = False

    def _need_detect_chars_globally(self, view: sublime.View) -> bool:
        return (
            is_view_normal_ready(view)
            and view_is_dirty_val(view)
            and not is_view_typing(view)
            and not is_view_too_large(view)
        )

    def _detect_chars_globally(self, view: sublime.View) -> None:
        char_regions = view_find_all_fast(view, global_get("char_regex_obj"), True)
        update_phantom_set(view, char_regions)
        log("debug", "Phantoms are re-rendered by detect_chars_globally()")