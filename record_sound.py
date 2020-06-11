import pyaudio
import wave
from array import array
import tqdm

class RecordingVoice(object):
    """docstring for RecodingVoice."""

    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.CHUNK = 1024
        self.RECORD_SECONDS = 1

    
    def save(self, frames, FILE_NAME):
        wavfile=wave.open(FILE_NAME, 'wb')
        wavfile.setnchannels(self.channels)
        wavfile.setsampwidth(self.audio.get_sample_size(self.format))
        wavfile.setframerate(self.rate)
        wavfile.writeframes(b''.join(frames)) #append frames recorded to file
        wavfile.close()
        return True


def record_sound():

    r = RecordingVoice()
    return r.record()


if __name__ == '__main__':
    r = RecordingVoice()
    print(r.record())
