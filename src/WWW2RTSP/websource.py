#!/usr/bin/python3
import argparse
import signal
import sys
from .screengrab_rtsp import ScreengrabConfig, create_mainloop, loop, \
    GstServer, ScreenGrabMediaFactory
from .offscreen_browser import OffscreenBrowser, Browsers


description = """
Open any given URL in an offscreen browser, grab it and stream it out via RTSP.

Xvfb is used for offscreen rendering.
As browser either chromium (in kiosk mode) or firefox (in fullscreen) is used. 
"""

_offscreen_browser = None


def do_cleanup():
    if _offscreen_browser is not None:
        _offscreen_browser.cleanup()


def exit_gracefully(signum, _):
    print('Signal handler called with signal', signum)
    try:
        do_cleanup()
    finally:
        sys.exit(1)


signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)


def process_args():
    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass

    parser = argparse.ArgumentParser(description=description, add_help=False, formatter_class=CustomFormatter)
    parser.add_argument("-p", "--rtsp-port", type=int, help="%(type)s: port to listen for rtsp requests", default=8554)
    parser.add_argument("-l", "--rtsp-label", type=str, help="%(type)s: label of provided rtsp stream", default="Stream1")
    parser.add_argument("-f", "--framerate", type=int, help="%(type)s: framerate to stream with", default=30)
    parser.add_argument("-w", "--width", type=int, help="%(type)s: width of the browser window", default=1920)
    parser.add_argument("-h", "--height", type=int, help="%(type)s: height of the browser window", default=1080)
    parser.add_argument("-b", "--browser", type=Browsers, help="browser to use",  choices=list(Browsers), default=Browsers.CHROMIUM.value)
    parser.add_argument("url", type=str, help="%(type)s: url of the site to open")

    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        parser.print_help()
        sys.exit(1 if len(sys.argv) == 1 else 0)
    return parser.parse_args()


def main():
    global _offscreen_browser
    args = process_args()
    _offscreen_browser = OffscreenBrowser(args.url, args.browser, args.width, args.height)
    print("browser started on display: :{}".format(_offscreen_browser.display))
    create_mainloop()
    rtsp_server = GstServer()
    grab_opts = ScreengrabConfig(width=args.width, height=args.height, framerate=args.framerate)
    print("starting screengrab")
    print("rtsp port:{} label:{}".format(rtsp_server.server.get_service(), args.rtsp_label))
    print("grab config:", grab_opts)
    stream = ScreenGrabMediaFactory(grab_opts)
    rtsp_server.attach_factory(stream, args.rtsp_label)
    loop()

# use this only via www2rtsp.sh, else you will get import errors...
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e, file=sys.stderr)
        do_cleanup()