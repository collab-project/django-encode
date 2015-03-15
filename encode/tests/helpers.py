# Copyright Collab 2012-2015

"""
Utilities and test data.
"""

from __future__ import unicode_literals

import shutil
from io import BytesIO

from django.conf import settings
from django.db.utils import IntegrityError

from django_webtest import WebTest


def encoders():
    """
    Define and return :py:class:`encode.models.Encoder` model data used for
    testing.
    """
    from encode.models import Encoder
    ffmpeg = Encoder()
    ffmpeg.name = "FFmpeg"
    ffmpeg.description = "FFmpeg is a complete, cross-platform solution to record, convert and stream audio and video."
    ffmpeg.documentation_url = "https://ffmpeg.org/ffmpeg.html"
    ffmpeg.path = "ffmpeg"
    ffmpeg.klass = "encode.encoders.FFMpegEncoder"

    convert = Encoder()
    convert.name = "convert (ImageMagick)"
    convert.description = "Converts between image formats as well as resize an image, blur, crop, despeckle, dither, draw on, flip, join, re-sample, and much more."
    convert.documentation_url = "http://www.imagemagick.org/script/convert.php"
    convert.path = "convert"

    return [ffmpeg, convert]


def encodingProfiles(ffmpeg, convert):
    """
    Define and return :py:class:`encode.models.EncodingProfile` model data
    used for testing.
    """
    from encode.models import EncodingProfile
    flash_video = EncodingProfile()
    flash_video.name = "Flash Video"
    flash_video.description = "The original Flash video container format. Also allows some other more exotic video codecs like On2 VP6 and Screen video."
    flash_video.mime_type = "video/x-flv"
    flash_video.container = "flv"
    # formats at http://flash.flowplayer.org/documentation/installation/formats.html
    # encoding html5 at http://www.adamish.com/blog/archives/496
    flash_video.video_codec = "FLV (Sorenson H.263)"
    flash_video.audio_codec = "MP3"
    flash_video.encoder = ffmpeg
    flash_video.command = '-c:v flv -c:a libmp3lame'

    flash_video2 = EncodingProfile()
    flash_video2.name = "Flash Video 2"
    flash_video2.description = "Similar to MP4, but Flash specific, or H.264/AAC in a FLV container. Useful for high-quality php-pseudostreaming, but rare otherwise."
    flash_video2.mime_type = "video/mp4"
    flash_video2.container = "f4v"
    flash_video2.video_codec = "H.264"
    flash_video2.audio_codec = "AAC"
    flash_video2.encoder = ffmpeg
    flash_video2.command = '-s 320x240 -r 30000/1001 -b 200k -bt 240k -vcodec libx264 -vpre ipod320 -acodec libfaac -ac 2 -ar 48000 -ab 192k'

    mp4 = EncodingProfile()
    mp4.name = "MP4"
    mp4.description = "MPEG-4 Part 14 or MP4 (formally ISO/IEC 14496-14:2003) is a multimedia container format standard specified as a part of MPEG-4. It is most commonly used to store digital video and digital audio streams, especially those defined by MPEG, but can also be used to store other data such as subtitles and still images."
    mp4.mime_type = "video/mp4"
    mp4.container = "mp4"
    mp4.video_codec = "H.264"
    mp4.audio_codec = "AAC"
    mp4.encoder = ffmpeg
    # see https://ffmpeg.org/trac/ffmpeg/wiki/x264EncodingGuide
    mp4.command = '-c:v libx264 -preset:v veryfast -crf 22 -ac 2 -c:a libfdk_aac'

    webm_av = EncodingProfile()
    webm_av.name = "WebM Audio/Video"
    webm_av.description = "WebM is an open, royalty-free, media file format designed for the web. WebM files consist of video streams compressed with the VP8 video codec and audio streams compressed with the Vorbis audio codec. The WebM file structure is based on the Matroska container."
    webm_av.mime_type = "video/webm"
    webm_av.container = "webm"
    webm_av.video_codec = "VP8"
    webm_av.audio_codec = "Vorbis"
    webm_av.encoder = ffmpeg
    webm_av.command = '-c:v libvpx -c:a libvorbis'

    # supported by chrome, firefox, opera
    webm_audio = EncodingProfile()
    webm_audio.name = "WebM Audio"
    webm_audio.description = "WebM is an open, royalty-free, media file format designed for the web. WebM files consist of video streams compressed with the VP8 video codec and audio streams compressed with the Vorbis audio codec. The WebM file structure is based on the Matroska container."
    webm_audio.mime_type = "audio/webm"
    webm_audio.container = "webm"
    webm_audio.audio_codec = "Vorbis"
    webm_audio.encoder = ffmpeg
    webm_audio.command = '-ab 128k -c:a libvorbis'

    ogg_av = EncodingProfile()
    ogg_av.name = "Ogg Audio/Video"
    ogg_av.description = "Ogg is a free, open container format maintained by the Xiph.Org Foundation. The creators of the Ogg format state that it is unrestricted by software patents[4] and is designed to provide for efficient streaming and manipulation of high quality digital multimedia."
    ogg_av.mime_type = "video/ogg"
    ogg_av.container = "ogv"
    ogg_av.video_codec = "Theora"
    ogg_av.audio_codec = "Vorbis"
    ogg_av.encoder = ffmpeg
    ogg_av.command = '-ab 128k -c:v libtheora -c:a libvorbis -vb 1000k'

    # supported by chrome, firefox, opera
    ogg_audio = EncodingProfile()
    ogg_audio.name = "Ogg Audio"
    ogg_audio.description = "Ogg is a free, open container format maintained by the Xiph.Org Foundation. The creators of the Ogg format state that it is unrestricted by software patents[4] and is designed to provide for efficient streaming and manipulation of high quality digital multimedia."
    ogg_audio.mime_type = "audio/ogg"
    ogg_audio.container = "oga"
    ogg_audio.audio_codec = "Vorbis"
    ogg_audio.encoder = ffmpeg
    # see http://pastebin.com/TwQZkeVf
    ogg_audio.command = '-f ogg -vn -sn -c:a libvorbis'

    png_image = EncodingProfile()
    png_image.name = "PNG"
    png_image.description = "Portable Network Graphics (PNG) is  is a bitmapped image format that employs lossless data compression. PNG was created to improve upon and replace GIF (Graphics Interchange Format) as an image-file format not requiring a patent license."
    png_image.mime_type = "image/png"
    png_image.container = "png"
    png_image.encoder = convert
    png_image.command = '"{input}" -size 320x240 "{output}"'

    # supported by chrome, ie, Safari on iOS
    mp3_audio = EncodingProfile()
    mp3_audio.name = "MP3 Audio"
    mp3_audio.description = "MP3, is a patented encoding format for digital audio which uses a form of lossy data compression. It is a common audio format for consumer audio storage, as well as a de facto standard of digital audio compression for the transfer and playback of music on most digital audio players."
    mp3_audio.mime_type = "audio/mpeg"
    mp3_audio.container = "mp3"
    mp3_audio.audio_codec = "MP3"
    mp3_audio.encoder = ffmpeg
    # see https://ffmpeg.org/trac/ffmpeg/wiki/Encoding%20VBR%20%28Variable%20Bit%20Rate%29%20mp3%20audio
    mp3_audio.command = '-q:a 2'

    return [flash_video, flash_video2, mp4, webm_av, webm_audio, ogg_av,
            ogg_audio, png_image, mp3_audio]


class DummyDataMixin(object):
    """
    Creates test encoders and encoding profiles.
    """
    def setUp(self):
        self.encoders = encoders()
        for encoder in self.encoders:
            try:
                encoder.save()
            except IntegrityError:
                pass
        self.profiles = encodingProfiles(ffmpeg=self.encoders[0],
            convert=self.encoders[1])
        for profile in self.profiles:
            try:
                profile.save()
            except IntegrityError:
                pass


class FileTestCase(WebTest):
    """
    Cleans up files after itself.
    """
    def setUp(self):
        WebTest.setUp(self)

        self.inputFileField = "input_file"

    def tearDown(self):
        WebTest.tearDown(self)

        # remove content of MEDIA_ROOT recursively
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def createTempFile(self, prefix, model, profiles, data):
        """
        Create :py:class:`encode.util.TemporaryMediaFile`.
        """
        from encode.util import parseMedia, TemporaryMediaFile
        tempFile = TemporaryMediaFile(
            prefix=prefix,
            model=model,
            inputFileField=self.inputFileField,
            profiles=profiles
        )
        fileData = BytesIO(parseMedia(data))
        result = tempFile.save(fileData)

        return result


#: base64-encoded string of some PNG image data
PNG_DATA = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAQCAYAAAAMJL+
VAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3QIaAAItUPl/PQ
AAAGdJREFUOMvt1CESglAQgOHvbcXkDBmvpGchWoicRwtH8CBcAZsYMFtg2/tnNn87G7bgjB5XnPCxr
8CCJ0aYsCbNK3CRVxcHnORfa0iuAhWowAZkIiUwJwJzQYs7bmh+X3DX1njjgeELJtkjwRJQ7r0AAAAA
SUVORK5CYII="""

#: base64-encoded string of some GIF image data
GIF_DATA = """data:image/gif;base64,R0lGODlhAwADAIABAMzMzP///yH5BAEAAAEALAAAAAA
DAAMAAAIERB5mBQA7"""

#: base64-encoded string of some WebM video data
WEBM_DATA = """data:video/webm;base64,GkXfowEAAAAAAAAfQoaBAUL3gQFC8oEEQvOBCEKCh
HdlYm1Ch4ECQoWBAhhTgGcBAAAAAAADZBFNm3RALE27i1OrhBVJqWZTrIHfTbuMU6uEFlSua1OsggEw
TbuMU6uEHFO7a1OsggNH7AEAAAAAAACkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAVSalmAQAAAAAAAEUq17GDD0JATYCNTGF2ZjU1LjEzLjEwMldBjUxhdmY1NS4xMy4x
MDJzpJApuiWk/ebsrrkJggwmlvbkRImIQKF4AAAAAAAWVK5rAQAAAAAAADuuAQAAAAAAADLXgQFzxYE
BnIEAIrWcg3VuZIaFVl9WUDiDgQEj44OEAXsZsOABAAAAAAAABrCBCrqBCh9DtnUBAAAAAAABxOeBAK
NAv4EAAICwAwCdASoKAAoAAEcIhYWIhYSIAgICdQOAfxgYyrrxurgfssjlNdD+9+HZ3Nf5VmsS/+d3/
lbWnOhK/kfw1/Nx9efBfR/ev/+pLCEL/Y1vC/a//seTgzzNAf/DCebfkPqr7j5/63kHdo081oPUX/Hb
+6M+F8a6HzVnz9I/ehnsHjsvW6YMhNq+DvLmRazCZ6b/8k24z/dSrtofoMNFhJlF4oyfmPQnZaNyDHJ
KYiZu7K9qSyJkNywuvEgAo9GBAb8AsQEAARAQABgAMCgv9AAgAP7YC/8ddyPA1/S/tz6cEBrQ77O6iZ
OJPZv5e1prIWnew821dlmAIpVLBXiWmiWa7CTlhi90cXgHi1BAMACjqoECnwCxAQABEBAAGAAwKC/0A
CAAxj9EsHv8ky8WrJVCY1IBI0muAA8wAKP+gQijAHECAAkQEAAY60yI4/1YAeUP44cAIAD8cL1Pkmgz
0AJfUKzFpcfc6T4cxWxv7UkGduaMvF/vnf//y5/MqLvrHwOhJ5O5qv3u/5DS/wp/wV7OP+J3SGa35Tv
5n8+93vl6tcl3CfxezyBJxoYUX6C/QAhDMoMDS7VPrBIAHFO7awEAAAAAAAARu4+zgQC3iveBAfGCAX
fwgQM="""

#: base64-encoded string of some WAV audio data
WAV_DATA = """data:audio/wav;base64,UklGRuIXAABXQVZFZm10IBAAAAABAAIAIlYAAESsAAA
CAAgAZGF0Yb4XAAB/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f3
9/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f
39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/
f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39
/f39/f39/f39/f4CAf39/f39/f3+AgH9/f3+EhH5+d3d7e3NziIh3d4iIgYGjo5yci4toaGBghoacnH
5+enqtrZ+fenqtrVVVRkZ3d2Jic3NVVUNDKCgeHjExfn5HRxQUJiYpKTc3t7eXl2RkYmKGhouLpqbPz
7Oz1NSkpICAXl6np6urtbXKyvb21dXi4tjY1tbZ2dHR0dG7u4ODm5vAwMDAWlpHR0NDDg4zMykpKCgQ
ED8/JiYsLDMzJiYQEB4ePz9jYwoKDg4/Pzg4GRlBQUhIa2tYWHh4xMTDw66uqKiysr+/09PU1O7u5OT
f3+Hh4+Pg4N/f3Nzb293d2NjW1svLs7Ouro+Pnp6QkFpaCwsKCjQ0NTUbGxsbHx8bGxwcGhotLSQkGR
kyMi8vGRkfHysrUFBkZENDIyMmJo2Nn5+oqOHhzMyjo7W1xcXw8Orq4uLj4+Tk4ODg4OPj3t7d3dra2
trW1ry8xcXc3KenhYVlZUVFU1NNTTc3LCwyMiEhGxsiIh8fHBwpKSQkHR0tLS8vMDBAQEhIQ0M9PVhY
R0dRUW1tmpqcnI6Oj4+9vd3d7Ozg4OLi4ODc3N7e09Pe3uDg29ve3tDQuLimpqensLClpaWlo6N0dGN
jcHBzc2BgQEA1NR4eHBw1NRwcGxshIR8fICAiIiQkMjJjY1hYUVFJSUhIUlJiYnl5jIyXl7CwsrKoqL
6+3d3l5dzc5OTf397e3t7g4ODg2NjFxbW1np6np66ut7ewsIuLcXF0dG9vcHCEhHx8a2tRUUdHMDAnJ
zs7PDwhISEhISEeHiQkJSUxMUpKSkpDQ1VVZWV9fY2NnZ2Pj4ODlJSyssDA4ODh4d7eyMjGxsPD1dXf
39vbv7+5uaurnZ2dnaOjnJyXl5GRgICFhYGBeHh+fnt7Y2NeXmBgZGRmZl1dRUU0NCsrLi4mJjIyPz8
9PTc3ODhCQk5OaWmHh42NgoKBgZ2doqKenqmpx8fIyLW1t7fBwcbGx8e6uqenoaGhoaqqsrKqqqKimp
qQkHh4dXV7e42NiYmGhnh4b29oaHFxcXFtbW5ubW1UVEpKUFBSUkpKOzs7O0BARkZUVGRkcXF0dHt7e
HhwcISEj4+srLCwr6+pqaSkmJiamqSksLCxsaysl5eSkpeXoKCcnJmZmpqQkImJi4uMjIGBgoJ4eHR0
bm5zc35+jIyBgXV1ZmZhYWBgamp1dW9vampoaFVVT09aWl9fXl5xcXl5dHRwcHh4hYWMjJCQjY2JiYS
ElZWhoaOjmZmNjYSEgYGQkKGhp6ehoZmZjY2JiY2NlZWUlJWVi4uFhXx8eHh6eoCAgoKBgXFxcXF1dY
GBiIiFhX9/bW1nZ2pqdXV5eXl5aGhfX1dXY2NqanJyeHh4eHp6dXVpaXBwdnaJiY2NjIyLi4WFhYWVl
ZSUlZWXl5CQj4+Tk6OjrKynp5OTjo6Li4+Pjo6Pj42NiIh+fnh4cHB7e4ODk5OUlI6OhIR8fHJyc3N4
eHt7dnZpaWJiX19hYWlpaGhTU1BQXFxdXVxcaGhxcXh4enp1dXh4hYWSkpubmpqZmYqKh4eSkqWlrq6
3t7Ozo6OdnZubm5ubm5SUhYWFhYyMiIiHh4+PkJCGhn19enp9fYiIjIyEhHt7cnJdXVtbX19kZGpqYG
BXV0lJR0dISFdXXFxcXGFhZ2dxcXl5fn6QkJOTiIiDg4uLmZmrq7Gxra2oqJ2dnp6lpbGxtLSzs5+fm
JiPj42Nj4+UlJWVj4+Dg35+e3t6ent7f3+AgHd3aWlra2traWlpaV5eV1dNTUlJS0tcXGBgXl5ZWVVV
U1NhYWxsf39/f4uLjY2Hh4qKjo6bm6qqrKympqCgoaGnp6ursrKurqmpo6OhoZ+fpaWlpZSUhYV/f3p
6e3uBgYCAe3t2dmlpZGRhYWVlampsbGhoXFxXV1VVVlZaWmVlYWFgYFhYXl5kZGtrcHB0dHJydXWFhY
2NmpqhoZ+fl5eTk5OToKCnp7a2trawsKionp6dnaSkp6emppmZkZGIiIODgIB+fnp6dXVpaWdnZmZoa
G5ua2tmZltbWVlZWWNjbW10dGxsZmZbW1paXFxtbXNzd3dzc3BwcXFzc39/jY2QkJCQjY2OjpWVm5ui
oqmppqafn5+fo6OsrK6uqqqfn5eXioqKio+PkJCPj4iIdXVra2NjYmJmZmxsbW1paWNjYWFhYWVlb29
vb21taGhoaGxscnJycnNzcHBtbWxsb295eYKChoaEhIGBgYGDg4eHlJSioqKinp6bm5WVmJidnaWlo6
Ofn5iYlpaTk5SUkpKMjIGBenp1dXd3d3dycnFxaWlhYWFhZWVoaHFxdnZ1dWxsaWlmZm9vdXV/f319e
Hhvb25ucnJ6en19fn56enl5fX2CgoiIjo6OjomJiYmJiZGRmJigoJ+fnJyQkIyMjo6Wlpubnp6SkoqK
fn57e319g4ODg3t7dnZubmpqampubnBwbm5ra2trbGxycnZ2e3t5eXZ2bm5tbXFxe3t/f4CAenp2dnJ
ydHR9fYmJioqIiIaGgYGBgYSEjY2SkpKSkpKSko+PkpKVlZaWj4+NjYqKioqPj5GRkZGKioSEenp1dX
R0eXl8fHp6cnJubmlpaWlsbHV1enp4eHNzcnJycnR0eHh7e3p6d3d1dXh4fX2BgYKCf399fXl5fHyAg
ImJjo6NjYeHgoKAgIeHjY2Xl5WVkpKLi4mJi4uQkJSUlZWRkYqKh4eGhoODgoKBgXp6dnZwcG9vcHB2
dnR0cnJra2hoaGhxcXd3f39/f3t7cHBubnNzfX2AgIODgYF6enp6fHx/f4ODhISDg4GBgICCgoWFi4u
NjYyMiIiHh4uLkpKWlpmZmJiPj4eHh4eMjJGRkZGNjYeHfHx4eHZ2dXV1dXR0b29sbGtra2ttbXJydH
Rzc3FxcXFzc3l5e3t9fXt7dnZ1dXd3gICGhoaGgoJ/f3t7e3t+foaGiYmMjIqKiIiHh4qKjY2Tk5SUk
JCOjo6OkJCTk5OTkJCNjYWFgoKCgoWFg4N9fXZ2cXFqamtrbW1wcHJycnJsbGpqaWlubnJyeXl6end3
dHR0dHl5e3uCgoKCf398fH19gICHh4iIiYmFhYODg4OIiIyMkpKSko+PioqIiIiIj4+Tk5eXlZWMjIa
GhYWGhoaGh4eBgX19d3d1dXR0c3Nzc29vampoaGlpbGxubnNzc3NwcG9vb290dHh4f3+BgX9/fHx8fH
19hISHh4qKiIiHh4eHiIiJiYqKi4uLi4qKiYmKiouLjY2Ojo6OioqGhoWFiYmKio2NiYmFhX19enp7e
3t7fX15eXFxb29ra2trbGxubnBwcHBubm5ucHBycnV1enp7e3p6fHx9fYODhoaKioiIhoaDg4WFiIiO
jpCQjo6IiIeHhYWFhYqKjIyLi4iIhISDg4SEhYWHh4mJiIiEhIGBgYGBgYGBf395eXZ2cnJycnR0dnZ
2dnFxbGxqamtrbW10dHd3d3d3d3V1dnZ8fH9/hYWHh4eHhISFhYWFiYmKioyMiYmIiIeHiIiKiouLio
qFhYCAgICBgYODh4eIiIaGgoKAgIGBgYGCgoWFg4OBgXt7eXl5eXp6e3t4eHV1c3NycnJyc3N0dHNzc
nJzc3Nzd3d7e4CAgICAgH9/f3+CgoeHiYmLi4qKiIiFhYWFh4eKioqKiYmFhYODgYGBgYODg4ODg4GB
f39/f4GBg4OFhYKCgYF9fXx8fn6BgYKCgIB7e3h4dHR0dHd3eXl5eXh4c3NycnJydHR4eHt7fHx8fHt
7fHyAgIKChoaGhoWFg4ODg4aGioqKiomJhYWDg4KChISGhoiIh4eDg4CAfX19fX9/g4OEhIODgIB/f3
19f3+BgYKCgIB+fnx8e3t7e319fHx6enZ2dXV2dnd3eXl5eXh4d3d2dnV1eXl8fICAgoKCgoCAgICAg
ISEhoaIiIeHhoaFhYWFhoaIiIeHhYWEhIKCgoKDg4ODgoKBgX5+fX19fYCAgYGDg4GBgIB9fXx8fX1/
f4GBgIB/f3t7eXl4eHl5enp6enh4d3d2dnZ2d3d6ent7e3t6enp6fHyBgYODhYWFhYKCgYGBgYWFiYm
KiomJh4eEhIKCgoKEhISEhISCgoCAfn5+fn9/gICAgH9/fn59fX5+gICBgYGBgIB9fXt7fHx+fn9/f3
98fHp6dnZ1dXZ2eXl7e3p6eXl4eHd3enp7e39/gICBgYCAgICCgoWFhoaHh4eHhYWEhIWFh4eIiIeHg
4OCgoCAgICBgYKCg4OAgH19fHx8fH19fn6BgYGBgIB9fX19fX1/f39/f39+fnt7enp7e3x8e3t6enh4
d3d3d3l5e3t8fH19fHx7e3t7fX2BgYODhYWFhYSEg4ODg4WFiIiIiIeHhoaEhIODg4OEhISEgYF/f39
/fn5+fn9/gIB/f3x8e3t7e319gICAgICAf398fHp6enp8fH5+fn58fHt7eXl5eXl5e3t8fHt7e3t7e3
p6fX1+foCAgICAgICAgYGDg4aGh4eHh4aGg4ODg4SEhoaHh4eHhISCgoCAf39/f4CAgIB/f319fHx7e
3x8fX1+fn5+fX18fHx8fX1+fn9/fn58fHp6e3t8fH5+fn5+fnt7enp5eXt7fHx/f39/fn59fX5+fn5/
f4ODhISEhISEg4OEhIWFhoaHh4WFhISDg4ODhISEhISEgYF9fXx8fHx9fX19fn59fXt7eXl5eXt7fHx
+fn9/fn58fHt7fHx9fX5+fn59fXx8e3t9fX19fn5+fn19fHx8fH19fn6BgYKCgoKAgICAgYGDg4SEho
aGhoWFg4OCgoODhYWFhYSEgoKBgX9/f39/f35+fX18fHp6enp7e3t7fHx9fXx8e3t7e3t7fX1+foCAf
39+fnx8fHx9fX9/gICAgH5+fX19fX19fn5/f4CAf39/f39/gICBgYODg4ODg4KCgoKDg4SEhYWFhYOD
goKAgICAgYGCgoGBf399fXx8enp7e3x8fHx8fHt7enp6enx8fHx+fn5+fX19fX19fn6AgICAgIB+fn1
9fX1+foCAgYGAgH5+fX19fX19fn6BgYKCgYGAgICAgICCgoODhISDg4KCgYGBgYKCgoKDg4GBf39+fn
19fn5+fn5+fX17e3l5eXl6ent7fX19fX19fHx8fHx8fn5/f4CAgIB/f35+fn5/f4CAgYGAgH9/fn5/f
39/gICAgICAf39+fn9/gICBgYKCgoKBgYCAgICBgYKCg4ODg4KCgYF/f39/f3+AgICAfn59fXx8fHx8
fHx8fHx8fHt7e3t7e319fn5/f35+fn5+fn5+f3+BgYKCgYGAgH9/f39/f4CAgYGBgYCAf39+fn5+f3+
AgICAgIB/f39/gICBgYKCgoKBgYCAgICAgIGBgoKCgoCAf39+fn19fX1/f35+fn58fHt7enp7e3x8fX
19fX19fX19fX5+f3+AgICAgIB/f39/gICBgYKCgYGAgH9/fn5/f39/gYGAgICAfn5+fn5+f3+AgIGBg
YGAgH9/f3+AgIGBgoKCgoGBgIB/f4CAgICAgH9/fn59fXx8fX19fX5+fX18fHt7e3t8fH5+fn5/f39/
fn5+fn9/gICBgYGBgYGBgYCAf3+AgICAgICAgH9/f39+fn9/f3+AgH9/f39+fn5+f3+AgIGBgYGBgYC
Af39/f4CAgYGBgYCAf39+fn5+fn5+fn5+fn59fXx8fHx8fH19fX19fX19fX19fX5+gICAgICAgIB/f3
9/gICBgYKCgYGAgH9/fn5/f39/gICAgH9/fn5+fn5+f39/f4CAgIB/f39/f3+AgIGBgYGAgICAf39/f
4CAgICAgICAfn59fX19fX19fX5+fn59fXx8fHx8fH5+fn5/f39/f39/f39/gICBgYGBgICAgICAgICA
gIGBgYGAgH9/fn5+fn9/f3+AgICAf39+fn5+fn6AgICAgICAgH9/f39/f4CAgICAgICAf39+fn5+f39
/f35+fX19fXx8fHx9fX5+fn5+fn19fX19fX9/f3+AgICAgIB/f39/gICBgYGBgYGAgICAf39/f4CAgI
B/f39/fn5+fn5+fn5/f39/f39+fn5+fn5/f4CAgICAgH9/fn5+fn9/gICAgH9/fn5+fn19fX1+fn5+f
n59fX19fX19fX5+f39/f39/f39/f39/gICBgYGBgICAgH9/gICAgIGBgYGAgH9/fn5+fn5+f39/f39/
fn5+fn5+fn5/f39/f39/f35+f39/f4CAgICAgH9/f39+fn5+f39/f39/fn59fX19fX19fX5+fn5+fn5
+fn5+fn9/gICAgICAgICAgICAgICBgYGBgYGAgH9/f3+AgICAgIB/f35+fn5+fn5+fn5/f39/f39+fn
5+fn5/f4CAgIB/f39/f39/f39/gICAgH9/fn5+fn5+fn5/f35+fn59fX19fX1+fn5+f39/f39/fn5+f
n9/gICBgYGBgICAgH9/f3+AgIGBgYGAgH9/f39/f39/f39/f39/fn5+fn5+f39/f39/f39/f39/f39/
f4CAgICAgH9/f39/f39/f3+AgICAf39+fn5+fn5+fn9/f39+fn5+fn5+fn9/gICAgICAf39/f4CAgIC
BgYGBgICAgH9/f39/f4CAgICAgH9/fn5+fn5+f39/f39/f39+fn5+f39/f39/f39/f39/f39/f4CAgI
CAgH9/f39/f39/f39/f39/f39+fn5+fn5+fn9/f39/f39/f39/f39/gICAgICAgICAgICAgICAgICAg
IB/f39/f39/f39/f39/f39/fn5+fn5+f39/f39/f39/f39/f39/f4CAgICAgH9/f39/f39/f39/f39/
f39/f39/f39/f39/f39/f35+fn5/f39/gICAgH9/f39/f39/gICAgICAgICAgH9/f39/f4CAgIB/f39
/f39/f39/f39/f39/f39+fn9/f39/f39/f39/f39/f39/f39/gICAgH9/f39/f39/f39/f39/f39/f3
9/f39/f39/f39/f39/f39/f39/gICAgICAgIB/f39/gICAgICAgIB/f39/f39/f39/f39/f39/f39+f
n9/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/gICAgH9/f39/f39/f39/f39/f39/f39/f39/
f39/gICAgICAf39/f39/gICAgICAgICAgH9/f39/f4CAgIB/f39/f39/f39/f39/f39/f39/f39/f39
/f39/f39/f39/f39/f4CAgICAgH9/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/gI
CAgICAf39/f39/f3+AgICAgIB/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/g
IB/f39/f39/f4CAgICAgH9/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/gICAgICA
f39/f39/f39/f4CAf39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39
/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f3
9/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f
39/f39/f39/gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIA="""
