from flask import Flask, Response, render_template
import os
from record_sound import RecordingVoice
import json
import pyaudio
from array import array
import timeit
import shutil

WAVE_PATH = 'model/waves'

app = Flask(__name__)

if os.path.isdir(WAVE_PATH):
    shutil.rmtree(WAVE_PATH)
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

        while True:
            data = stream.read(r.CHUNK)
            
            if len(data) == 0:
                break
            data_chunk = array('h', data)
            vol = max(data_chunk)
            
            if(vol>0):
                frames.append(data) 
                r.save(frames, 'model/tmp.wav')
                r.save(frames, 'model/waves/tmp'+str(count)+'.wav') 
                count += 1
                print("finished recording")
                data_ = json.dumps(
                    {
                        'value': get_decode(),
                     }
                )
                print(data_)
                yield f"data:{data_}\n\n"
                #time.sleep()

    return Response(process(), mimetype='text/event-stream')


def record():
    r = RecordingVoice()
    return r.record()


def get_decode():
    model = 'C:/Users/manke/Documents/MSI/FlaskKaldi'
    command = "C:/Users/manke/Documents/MSI/kaldi/kaldiwin_vs2017_OPENBLAS_prev/x64/Debug/online-wav-gmm-decode-faster " \
              "--rt-min=0.3 --rt-max=0.5 --max-active=40000 --beam=12.0 --acoustic-scale=0.0769 " \
              "scp:./model/wav1.scp ./model/final.mdl ./model/HCLG.fst ./model/words.txt " \
              "1:2:3:4:5 ark,t:./model/trans.txt ark,t:./model/ali.txt"
    dec = os.popen(command)
    return dec.read()

if __name__ == '__main__':
    app.run(debug=True, threaded=True)



