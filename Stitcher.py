import tkinter as tk
import cv2
import threading
import socket
import os

class RTSPStitcher:
    def __init__(self, root):
        self.root = root
        self.root.title("RTSP Stream Stitcher")

        self.stream1_label = tk.Label(root, text="Stream 1 URL:")
        self.stream1_label.pack()
        self.stream1_entry = tk.Entry(root)
        self.stream1_entry.pack()

        self.stream2_label = tk.Label(root, text="Stream 2 URL:")
        self.stream2_label.pack()
        self.stream2_entry = tk.Entry(root)
        self.stream2_entry.pack()

        self.stream_name_label = tk.Label(root, text="Stream Name:")
        self.stream_name_label.pack()
        self.stream_name_entry = tk.Entry(root)
        self.stream_name_entry.pack()

        self.stitch_button = tk.Button(root, text="Stitch Streams", command=self.stitch_streams)
        self.stitch_button.pack()

        self.keep_alive_var = tk.BooleanVar()
        self.keep_alive_check = tk.Checkbutton(root, text="Keep Alive", variable=self.keep_alive_var)
        self.keep_alive_check.pack()

        self.output_label = tk.Label(root, text="Output URL:")
        self.output_label.pack()
        self.output_entry = tk.Entry(root)
        self.output_entry.pack()

        self.log_label = tk.Label(root, text="Logs:")
        self.log_label.pack()
        self.log_text = tk.Text(root, height=5, width=40)
        self.log_text.pack()

    def stitch_streams(self):
        stream1_url = self.stream1_entry.get()
        stream2_url = self.stream2_entry.get()
        stream_name = self.stream_name_entry.get()

        if not stream1_url or not stream2_url or not stream_name:
            self.log_text.insert("end", "Please provide both stream URLs and a stream name.\n")
            return

        host_ip = socket.gethostbyname(socket.gethostname())
        rtsp_port = 8554  # Modify the RTSP port as needed

        output_url = f"rtsp://{host_ip}:{rtsp_port}/{stream_name}"
        self.output_entry.delete(0, "end")
        self.output_entry.insert("end", output_url)
        self.log_text.insert("end", "Stitching and streaming started...\n")

        # Attempt to determine VideoWriter settings from the first input stream
        cap1 = cv2.VideoCapture(stream1_url)
        frame_width = int(cap1.get(3))
        frame_height = int(cap1.get(4))
        frame_rate = int(cap1.get(5))
        cap1.release()

        # Example stitching and streaming logic using OpenCV:
        def stitch_and_stream():
            while self.keep_alive_var.get():
                try:
                    cap1 = cv2.VideoCapture(stream1_url)
                    cap2 = cv2.VideoCapture(stream2_url)

                    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # XVID codec
                    out = cv2.VideoWriter(output_url, fourcc, frame_rate, (frame_width * 2, frame_height))

                    while True:
                        ret1, frame1 = cap1.read()
                        ret2, frame2 = cap2.read()

                        if not ret1 or not ret2:
                            break

                        stitched_frame = cv2.hconcat([frame1, frame2])
                        out.write(stitched_frame)

                        if not self.keep_alive_var.get():
                            break

                    cap1.release()
                    cap2.release()
                    out.release()

                    self.log_text.insert("end", "Stitching and streaming completed.\n")
                except Exception as e:
                    self.log_text.insert("end", f"Error: {e}\n")

        # Check for duplicate instances
        if not self.is_instance_running(stream_name):
            threading.Thread(target=stitch_and_stream).start()
        else:
            self.log_text.insert("end", "Duplicate instance detected. Cannot start.\n")

    def is_instance_running(self, stream_name):
        output_url = f"rtsp://{socket.gethostbyname(socket.gethostname())}:{8554}/{stream_name}"
        return os.path.exists(output_url)

if __name__ == "__main__":
    root = tk.Tk()
    app = RTSPStitcher(root)
    root.mainloop()
