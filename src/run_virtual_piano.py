from mediawebcore.core import run_server
from piano_position_plugin import PianoPositionPlugin

plugin = PianoPositionPlugin()

run_server(
    on_frame=plugin.on_frame,
    video_size_input=["80%", "40%"],
    video_size_output=["80%", "40%"],
    layout="top-bottom",
    render_mode="bottom",
    audio_send=False,
    audio_receive=False
)