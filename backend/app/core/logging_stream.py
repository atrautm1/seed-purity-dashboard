import logging
import asyncio


class QueueLogHandler(logging.Handler):
    def __init__(self, log_queue: asyncio.Queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        try:
            log_entry = self.format(record)
            # Push into the queue non-blockingly
            self.log_queue.put_nowait(log_entry + "\n")
        except Exception:
            self.handleError(record)
