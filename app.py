from flask import Flask, Response, render_template
import os
from record_sound import RecordingVoice
import json
import pyaudio
from array import array
import time
import shutil
import numpy as np
from datetime import datetime

WAVE_PATH = 'data/waves'

app = Flask(__name__)

if not os.path.isdir(WAVE_PATH):
    os.makedirs(WAVE_PATH)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/decode')
def decode():
    print("start decoding")
    def process():
        r = RecordingVoice()
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=r.CHUNK)
        stream.start_stream()
        count = 0
        frames = []
        date_time = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
        current_path = WAVE_PATH + '/' + date_time
        os.makedirs(current_path)

        while True:
            data = stream.read(r.CHUNK)
            data_chunk = np.frombuffer(data, dtype='B')
            print(data_chunk)
            vol = max(data_chunk)
            if(vol > 100):
                frames.append(data) 
                r.save(frames, 'data/tmp.wav')
                count += 1
                r.save(frames, current_path + '/tmp'+str(count)+'.wav')
                print("finished recording")
                decoded_str = get_decode()
                print(decoded_str,  file=open(current_path + '/tmp'+str(count)+'.txt', 'w')) 
                
                with open(current_path + '/tmp'+str(count)+'.txt', encoding = "utf8") as file:
                    decoded_str = file.read().replace('\n', '')
                
                data_ = json.dumps(
                    {
                        'value': decoded_str
                     }
                )
                print(data_)
                yield f"data:{data_}\n\n"
                

    return Response(process(), mimetype='text/event-stream')
    

def record():
    r = RecordingVoice()
    return r.record()


def get_decode():
    command = "online-wav-gmm-decode-faster " \
              "--rt-min=0.3 --rt-max=0.5 --max-active=4000 --beam=12.0 --acoustic-scale=0.0769 " \
              "scp:./data/wav.scp ./model/final.mdl ./model/HCLG.fst ./model/words.txt " \
              "1:2:3:4:5 ark,t:./model/trans.txt ark,t:./model/ali.txt"
    dec = os.popen(command)
    return dec.read()

if __name__ == '__main__':
    app.run(debug=True, threaded=True)



