from PySide6.QtCore import QThread, Signal
import queue


class CaptureConsoleOutputThread(QThread):
    """ Captures the contents that would normally be written to the console and emmits them as a signal to the GUI. """

    output_written = Signal(str)  # Signal to update GUI

    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.running = True

    def write(self, text):
        if text.strip():
            self.queue.put(text)

    def run(self):
        """ Continuously check for new console output and emit it. """
        while self.running:
            try:
                text = self.queue.get(timeout=0.1)
                self.output_written.emit(text)
            except queue.Empty:
                continue

    def stop(self):
        """ Stop capturing output """
        self.running = False
        self.quit()
        self.wait()

    def flush(self):
        pass  # Required for compatibility
