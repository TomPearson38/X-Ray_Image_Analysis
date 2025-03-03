import os
import threading
import stages.model_training
import torch
import gc


class YoloThread(threading.Thread):
    def __init__(self, output_yaml, weights, img_size, batch_size, epochs, event):
        self._running = False
        self.output_yaml = output_yaml
        self.weights = weights
        self.img_size = img_size
        self.batch_size = batch_size
        self.epochs = epochs
        self.trainYoloThread = threading.Thread(target=self.run, daemon=True)
        self.stop_flag = event

    def start(self):
        if self.trainYoloThread and self.trainYoloThread.is_alive():
            print("Thread is already running!")
            return

        self._running = True
        self.trainYoloThread.start()

    def run(self):
        stages.model_training.train_yolo(
            data_yaml=self.output_yaml,
            output_root=os.path.abspath("trained_models"),
            weights=self.weights,
            img_size=self.img_size,
            batch_size=self.batch_size,
            epochs=self.epochs
        )
        torch.cuda.empty_cache()
        torch._C._cuda_clearCublasWorkspaces()
        gc.collect()
        self.stop_flag()

    def stop(self):
        self._running = False
        if self.trainYoloThread:
            self.trainYoloThread.join()  # Ensure the thread stops before continuing
        print("Thread stopped.")
