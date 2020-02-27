from collections import deque

from kivy.input.managers import EventManagerBase


class HoverEventManager(EventManagerBase):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type_name = 'hover'
        self.dispatched_events = []
        self.waiting_events = deque()

    def update(self, etype, me):
        self.waiting_events.append((etype, me))

    def dispatch(self, *args):
        if not self.waiting_events and self.dispatched_events:
            # Dispatch copied event of last event dispatched
            last_event = self.dispatched_events[-1]
            event = type(last_event)(last_event.device, last_event.id, [0, 0])
            last_event.copy_to(event)
            self.waiting_events.append(('update', event))

        while self.waiting_events:
            etype, me = self.waiting_events.popleft()
            self.dispatched_events.append(me)
            if not me.grab_exclusive_class:
                for listener in self.event_loop.event_listeners:
                    listener.dispatch('on_motion', etype, me)

            # Handle grabbed events
            if len(self.dispatched_events) < 2:
                return
            current = self.dispatched_events[-1]
            prev = self.dispatched_events[-2]
            for weak_widget in prev.grab_list:
                if weak_widget not in current.grab_list:
                    # Notify widgets that are no longer handled by current
                    # hover event
                    widget = weak_widget()
                    if widget:
                        widget.dispatch('on_motion', 'end', current)
            self.dispatched_events.pop(0)
