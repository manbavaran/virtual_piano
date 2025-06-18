import eventlet
eventlet.monkey_patch()

from mediawebcore.core import run_server
from piano_position_plugin import PianoPositionPlugin
import os

plugin = PianoPositionPlugin()

run_server(
    on_frame=plugin.on_frame,
    video_size_input=["80%", "40%"],
    video_size_output=["80%", "40%"],
    layout="top-bottom",
    template="index.html",
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    audio_send=False,
    audio_receive=False
)