import subprocess as sp
import time
from typing import List, Optional
import platform

import numpy as np


class RtspPush:
    __rtst_url: str = ""
    __opened: bool = False

    __command: List[str]
    __params_encoder: List[str]
    __width: int
    __height: int
    __fps: float

    __last_time: Optional[time.time] = None

    __p: Optional[sp.Popen] = None

    interval: bool = True

    __open_have_error: bool = False

    def __init__(
            self,
            rtsp_url: str,
            width: int = 1920,
            height: int = 1080,
            fps: float = 30,
            interval: bool = True
    ):
        self.__rtst_url = rtsp_url

        self.__command = []
        self.__params_encoder = []

        self.__width = width
        self.__height = height
        self.__fps = fps
        self.interval = interval

        self.set_recommend_encoder()

        self.update_command()

    @staticmethod
    def check() -> bool:
        # Check is ffmpeg installed
        try:
            sp.run(["ffmpeg", "-version"], capture_output=True)

            return True
        except FileNotFoundError:
            print("ffmpeg not found")
            return False
        except sp.CalledProcessError:
            print("ffmpeg can't run")
            return False
        except Exception as e:
            print(e)
            return False

    @property
    def is_opened(self) -> bool:
        return self.__opened

    @property
    def rtsp_url(self) -> str:
        return self.__rtst_url

    @property
    def width(self) -> int:
        return self.__width

    @width.setter
    def width(self, width: int):
        if self.is_opened:
            return

        self.__width = width

        self.update_command()

    @property
    def height(self) -> int:
        return self.__height

    @height.setter
    def height(self, height: int):
        if self.is_opened:
            return

        self.__height = height

        self.update_command()

    @property
    def fps(self) -> float:
        return self.__fps

    @fps.setter
    def fps(self, fps: float):
        if self.is_opened:
            return

        self.__fps = fps

        self.update_command()

    def set_recommend_encoder(self):
        # Is Linux
        if self.is_linux():
            # Get GPU List
            gpu_text = sp.run(["lspci", "-v"], capture_output=True, text=True).stdout

            # Check Intel GPU
            # if "Intel Corporation" in gpu_text:
            #     self.set_encoder_gpu_intel()

            # Check Nvidia GPU
            if "NVIDIA Corporation" in gpu_text:
                self.set_encoder_gpu_nvidia()

            # Check AMD GPU
            if "Advanced Micro Devices, Inc." in gpu_text:
                self.set_encoder_gpu_amd()

        elif self.is_macos():
            self.set_encoder_cpu()
        else:
            self.set_encoder_cpu()

    def set_encoder_cpu(self):
        self.__params_encoder = [
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
        ]

    def set_encoder_gpu_intel(self):
        self.__params_encoder = [
            '-c:v', 'h264_qsv',
        ]

        self.update_command()

    def set_encoder_gpu_nvidia(self):
        self.__params_encoder = [
            '-c:v', 'h264_nvenc',
        ]

        self.update_command()

    def set_encoder_gpu_amd(self):
        self.__params_encoder = [
            '-c:v', 'h264_amf',
        ]

        self.update_command()

    def update_command(self):
        width = self.width
        height = self.height
        fps = self.fps

        rtsp_url = self.rtsp_url

        default_encoder = [
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
        ]

        params_encoder = self.__params_encoder.copy()
        if len(params_encoder) == 0:
            params_encoder = default_encoder

        command = [
            'ffmpeg',
            '-y',  # 覆盖输出文件而不询问
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', "{}x{}".format(width, height),
            '-r', str(fps),  # 帧率
            '-i', '-',  # 输入来自标准输入

            *params_encoder,

            '-pix_fmt', 'yuv420p',
            '-rtsp_transport', 'tcp',
            '-f', 'rtsp',
            rtsp_url
        ]

        self.__command = command

    def open(self) -> bool:
        try:
            self.update_command()
            command = self.__command
            self.__p = sp.Popen(command, stdin=sp.PIPE)

            self.__opened = True

            return True
        except Exception as e:
            print(e)

            __open_have_error = True
            self.__opened = False

            return False

    def close(self):
        if self.is_opened:
            try:
                self.__p.stdin.close()

                self.__open_have_error = False
                self.__opened = False
            except Exception as e:
                print(e)

    def __before_push(self) -> bool:
        if not self.is_opened:
            # If last open not have error, try open again
            if not self.__open_have_error:
                if self.open():
                    return True

            return False

        return True

    def push_cv2(self, frame):
        if not self.__before_push():
            return

        if self.interval and self.__last_time is not None:
            elapsed_time = time.time() - self.__last_time
            frame_interval = 1 / self.fps
            if elapsed_time < frame_interval:
                time.sleep(frame_interval - elapsed_time)

        try:
            self.__p.stdin.write(frame.tobytes())
        except Exception as e:
            print(e)

        self.__last_time = time.time()

    def push_pillow(self, image, convert_to_bgr: bool = True):
        if not self.__before_push():
            return

        cv2_data = np.array(image)

        if convert_to_bgr:
            # Convert to BGR format
            cv2_data = cv2_data[:, :, ::-1]

        self.push_cv(cv2_data)

    push_cv = push_cv2
    push = push_cv

    def install(self) -> bool:
        if self.check():
            print("ffmpeg is installed")
            return True
        elif self.is_linux():
            # sudo apt install ffmpeg -y
            command = "sudo apt install ffmpeg -y"
            sp.run(command, shell=True)
            return self.check()
        elif self.is_windows():
            print("Installer is not implemented on Windows")
        else:
            print("Unknown OS")

    @staticmethod
    def is_linux() -> bool:
        return platform.system() == "Linux"

    @staticmethod
    def is_windows() -> bool:
        return platform.system() == "Windows"

    @staticmethod
    def is_macos() -> bool:
        return platform.system() == "Darwin"

    def __del__(self):
        self.close()
