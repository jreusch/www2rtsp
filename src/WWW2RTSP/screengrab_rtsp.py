#!/usr/bin/python3
import gi
from collections import namedtuple

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject

__init = False
__loop = None

DEFAULT_RTSP_LABEL = "Stream1"

_ConfigFields = {"width": 1920,
                 "height": 1080,
                 "framerate": 60}

# with python 3.7+ both lines can be combined to
#namedtuple('..', _ConfigFields.keys(), defaults=_ConfigFields.values())
ScreengrabConfig = namedtuple("ScreengrabConfig", _ConfigFields.keys())
ScreengrabConfig.__new__.__defaults__ = tuple(_ConfigFields.values())


def create_mainloop():
    global __init, __loop

    if __init:
        raise Exception("mainloop already created")
    __loop = GObject.MainLoop()
    GObject.threads_init()
    Gst.init(None)

    __init = True


class ScreenGrabMediaFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, grab_opts: ScreengrabConfig):
        GstRtspServer.RTSPMediaFactory.__init__(self)
        self.grab_opts = grab_opts

    def do_create_element(self, url):
        # s_src = "v4l2src ! video/x-raw,rate=30,width=320,height=240 ! videoconvert ! video/x-raw,format=I420"
        # s_src = "ximagesrc use-damage=0 ! video/x-raw,framerate=30/1 ! videoscale method=0 ! videoconvert"
        # s_h264 = "videoconvert ! vaapiencode_h264 bitrate=1000"
        # s_src = "videotestsrc ! video/x-raw,rate=30,width=320,height=240,format=I420"
        #s_src = "ximagesrc use-damage=1 show-pointer=0 ! video/x-raw,framerate={opt.framerate}/1,height={opt.height},width={opt.width} ! videoconvert".format(
        #    opt=self.grab_opts)
        s_src = "ximagesrc use-damage=0 show-pointer=0 ! video/x-raw,framerate={opt.framerate}/1,height={opt.height},width={opt.width} ! videoconvert ! video/x-raw,format=I420 ".format(
            opt=self.grab_opts)
        #s_h264 = "x264enc tune=zerolatency"
        #s_h264 = "vaapih264enc rate-control=cbr tune=high-compression"
        s_h264 = "vaapih264enc rate-control=cbr"

        #s_h264 = "omxh264enc ! \"video/x-h264,profile=high\" ! h264parse "
        #s_h264 = "omxh264enc ! h264parse "
        #s_h264 = "omxh264enc ! h264parse "
        pipeline_str = "( {s_src} ! queue max-size-buffers=1 name=q_enc ! {s_h264} ! rtph264pay name=pay0 pt=96 )".format(
            **locals())
        #pipeline_str = "( videotestsrc ! video/x-raw,framerate=30/1,height=480,width=640 ! videoconvert ! omxh264enc ! h264parse ! rtph264pay  name=pay0 config-interval=1 pt=96 )"
        print(pipeline_str)
        return Gst.parse_launch(pipeline_str)


class GstServer():
    def __init__(self, port=8554):
        self.server = GstRtspServer.RTSPServer()
        self.server.set_service(str(port))
        self.server.attach(None)

    def attach_factory(self, factory: GstRtspServer.RTSPMediaFactory, label=DEFAULT_RTSP_LABEL):
        factory.set_shared(True)
        mounts = self.server.get_mount_points()
        mounts.add_factory("/{}".format(label), factory)


def loop():
    if not __init:
        raise Exception("mainloop not created")
    __loop.run()


if __name__ == '__main__':
    create_mainloop()
    rtsp_server = GstServer()
    grab_opts = ScreengrabConfig(width=640, height=480, framerate=30)
    print("starting screengrab")
    label = DEFAULT_RTSP_LABEL
    print("rtsp port:{} label:{}".format(rtsp_server.server.get_service(), label))
    print("grab config:", grab_opts)
    stream = ScreenGrabMediaFactory(grab_opts)
    rtsp_server.attach_factory(stream, label)
    loop()