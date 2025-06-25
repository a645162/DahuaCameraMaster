import argparse
import cv2

def start_viewer(server_url: str):
    cap = cv2.VideoCapture(server_url)
    while True:

        ret, frame = cap.read()
        if not ret:
            print("Can't read video stream")
            exit()

        # TODO: Add your code here

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def get_opts():
    parser = argparse.ArgumentParser()

    parser.add_argument("--url", "-u", type=str, default="")

    return parser.parse_args()


def main():
    opts = get_opts()

    server_url = str(opts.url).strip()

    if len(server_url) == 0:
        server_url = get_rtsp_server()

    if len(server_url) == 0:
        print("Please input the RTSP server url")
        exit(1)

    start_viewer(server_url)


if __name__ == "__main__":
    main()
