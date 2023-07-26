from keyboard import is_pressed
from os import remove

from pyautogui import screenshot
from numpy import array
from cv2 import VideoWriter_fourcc, VideoWriter, cvtColor, COLOR_RGB2BGR
from moviepy.editor import VideoFileClip, AudioFileClip
from pyaudio import paInt16, PyAudio
from wave import open
from pydub import AudioSegment


def get_dev_index(p: PyAudio):
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev["hostApi"] != 0:
            continue
        if "stereo mix" in f"{dev['name']}".lower():
            return i
    return None


def main():
    while True:
        # подключаемся к звуку системы
        
        p = PyAudio()
        dev_index = get_dev_index(p)
        
        if dev_index is None:
            raise ValueError('No Stereo Mix device is found')   
            return
        
        
        # аудиопараметры
        
        CHANNELS = 2
        RATE = 44100
        BUFFER = 4096
        
        stream = p.open(
            format=paInt16,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=dev_index,
            frames_per_buffer=BUFFER,
        )


        # запись

        print('Запись начата')
        
        screens, audios = [], []
        while not is_pressed('ctrl + q'):
            screens.append(array(screenshot()))
            audios.append(stream.read(BUFFER))
            
            
        # создание видео
        
        print('Создаю видео...')
            
        video = VideoWriter(
            'only video.mp4',
            VideoWriter_fourcc(*'mp4v'),
            14,
            screens[0].shape[:-1][::-1]
        )

        for screen in screens:
            bgr = cvtColor(screen, COLOR_RGB2BGR)
            video.write(bgr)

        video.release()
        
        
        # закрытие аудиопотоков
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        
        # создание аудиофайла
        
        print('Создаю аудио...')

        wave = open('only audio.wav', 'wb')
        wave.setnchannels(CHANNELS)
        wave.setsampwidth(p.get_sample_size(paInt16))
        wave.setframerate(RATE)
        wave.writeframes(b''.join(audios))
        wave.close()

        audio = AudioSegment.from_wav('only audio.wav')
        audio.export('only audio.mp3', format='mp3')
        remove('only audio.wav')
        
        
        # слияние аудио и видео
        
        VideoFileClip('only video.mp4').set_audio(AudioFileClip('only audio.mp3')).write_videofile('video.mp4')
        remove('only video.mp4')
        remove('only audio.mp3')
        
        print('Видео готово')
        input('-' * 42)
    

if __name__ == '__main__':
    main()
    