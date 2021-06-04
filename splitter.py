
"""
Remove silence from raw speech, split them and finally rename each splitted track to corresponding sentence.
@author: zil.ink/anvaari
"""


import pandas as pd
import os
from shutil import copyfile
from os.path import join as join_path
import speech_recognition as sr
from pydub import AudioSegment
from glob import glob
import progressbar
import Levenshtein
import re
from fa import convert
import hazm
from inaSpeechSegmenter import Segmenter
import argparse



project_dir=os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description='Remove silence from raw speech, split them and finally rename each splitted track to corresponding sentence.')
parser.add_argument(
"--audio-dir",
dest='audio_dir',
type=str,
help="Directiry include raw voice which aren't process and split yet.",
)

parser.add_argument(
"--csv-dir",
dest='csv_dir',
type=str,
help="[Optional] Directory include processed CSVs from inaSpeechSegmenter.",
)
parser.add_argument(
"--output-dir",
dest='output_dir',
default=project_dir,
type=str,
help="Directory which you want place output folder there. Default is project folder",
)

args = parser.parse_args()
audios_dir=args.audio_dir
csv_dir=args.csv_dir
output_dir=args.output_dir



if audios_dir is None :
    audios_dir=input('\naudios_dir not specify in the arguments. Please type audios_dir here.\n')
if csv_dir is None:
    csv_dir=join_path(output_dir,'Output','CSVs')

def check_preq_files():
    rais=0
    if not os.path.isdir(join_path(project_dir,'text')):
        rais=1
        print('\nYou should put folder with name "text" which contain original sentences of speech in it.\n')
    if not os.path.isfile(join_path(project_dir,'fa.py')):
        rais=1
        print('\nYou should put fa.py module in project directory (directory where this file exist there)\n')
    if not os.path.isfile(join_path(project_dir,'error_list.txt')):
        rais=1
        print('\nerror_list.txt file (which contain sentence which speaker dont read them) must exist in project directory\n')
    if rais:
        raise Exception("Please put mentioned files and folder in project directory")
    
    


def create_output_folder(output_dir):
    '''
    

    Parameters
    ----------
    output_dir : str
        Directory where we want output seat there.

    Returns
    -------
    None.
    Create "Output" folder : Main output folder
    Create "Output/Splitted" folder : Folder where splitted audio track will copy here
    Create "Output/Transcript" folder : Folder where CSVs contain transcript of splitted track 
    Create "Output/wavs" folder : Folder where Final Renamed audio which they are match with original sentences will copy here
    All in in output_dir directory.
    Create "Output/CSVs" folder : Folder where output CSVs of inaSpeechSegmenter will be save in it.
    
    '''
    # Main Folder
    if os.path.exists(join_path(output_dir,'Output')):
        pass
    else:
        os.mkdir(join_path(output_dir,'Output'))
    
    # Splitted Audio Track Folder
    if os.path.exists(join_path(output_dir,'Output','Splitted')):
        pass
    else:
        os.mkdir(join_path(output_dir,'Output','Splitted'))
    
    # Transcript Folder
    if os.path.exists(join_path(output_dir,'Output','Transcript')):
        pass
    else:
        os.mkdir(join_path(output_dir,'Output','Transcript'))
    
    # wavs Folder
    if os.path.exists(join_path(output_dir,'Output','wavs')):
        pass
    else:
        os.mkdir(join_path(output_dir,'Output','wavs'))
        
    # CSVs Folder
    if os.path.exists(join_path(output_dir,'Output','CSVs')) :
        pass
    elif  csv_dir==join_path(output_dir,'Output','CSVs'):
        os.mkdir(join_path(output_dir,'Output','CSVs'))
    
def track_name_extractor(file_name):
    '''
    

    Parameters
    ----------
    file_name : str
        file_name can be {track_name}.mp3, {track_name}.wav, {track_name}.csv,{track_name}_raw.mp3, {track_name}_raw.wav, {track_name}_raw.csv, directory to theese file.

    Raises
    ------
    
        track_name must made from only digits (0-9). If not, Exception will raise.

    Returns
    -------
    track_name : str
        name of audio track (extracted from csv or audio file or directory).

    '''
    if os.path.isdir(file_name):
        track_name=file_name[file_name.rfind('/')+1:]
        if not track_name.isdigit():
            raise 'File name incorrect'
        return track_name
    file_name=file_name[file_name.rfind('/')+1:]
    if 'raw' in file_name:
        track_name=file_name[:file_name.find('_')]
    else:
        track_name=file_name[:file_name.find('.')]
    if not track_name.isdigit():
        raise Exception('Incorrect file name')
    return track_name


def audio_segment(audios_dir,csv_dir):
    '''
    

    Parameters
    ----------
    audios_dir : str
        Directory to folder contain raw speech files.
    csv_dir : str
        Directory to folder contain csv file contain speech range of raw speechs .

    Returns
    -------
    None.
    Create CSVs contain speech range of speechs in csv_dir if not created before. 
    '''
    
    audios_dir_list=glob(join_path(audios_dir,'*.mp3'))
    created_csv=glob(join_path(csv_dir,'*.csv'))
    created_csv_name=list(map(track_name_extractor,created_csv))
    
    seg=Segmenter(vad_engine='smn',detect_gender=False)
    for audio_dir,i in zip(audios_dir_list,progressbar.progressbar(range(len(audios_dir_list)))):
        track_name=track_name_extractor(audio_dir)
        if track_name in created_csv_name:
            continue
        segment=seg(audio_dir)
        raw_segment=pd.DataFrame(segment,columns=['labels','start','stop'])
        raw_segment=raw_segment[raw_segment['labels']=='speech']
        raw_segment.reset_index(drop=True,inplace=True)
        if raw_segment.at[0,'start']==0:
            raw_segment.at[0,'start']=0.01
        raw_segment.to_csv(join_path(csv_dir,f'{track_name}.csv'),index=False,sep="	")

        
    




def audio_split(audio_file_dir,speech_range_csv):
    '''
    Parameters
    ----------
    audio_file_dir : str
        Directory to audio file we want split it.
    speech_range_csv : str
        Directory to csv file contain time range of speech
    splitted_save_dir : str
        Directiory where splitet audio file wil be saved

    Returns
    -------
    splitted_dir : list
    List contain directory to each splitted audio file

    '''
    create_output_folder(output_dir)
    check_preq_files()
    track_name=track_name_extractor(audio_file_dir)
    if os.path.exists(join_path(output_dir,'Output','Splitted',f'{track_name}')):
        pass
    else:
        os.mkdir(join_path(output_dir,'Output','Splitted',f'{track_name}'))
    song = AudioSegment.from_mp3(audio_file_dir)
    speech_range=pd.read_csv(speech_range_csv,sep="	")
    Output_dir=[]
    i=1
    for index,row in speech_range.iterrows():
        start=float(row['start'])*1000
        end=float(row['stop'])*1000
        if end-start >500:
            splitted_i=song[start:end]
            splitted_i.export(join_path(output_dir,'Output','Splitted',f'{track_name}',f'{i}.wav'),format='wav')
            i+=1
            





def transcribe_audios(audio_chunked_path):
    create_output_folder(output_dir)
    check_preq_files()
    
    csv_name=track_name_extractor(audio_chunked_path)
    PATH_TO_CURRENT_CSV = join_path(output_dir,'Output','Transcript',f'{csv_name}.csv')

    audios_sanitized = [f for f in os.listdir(audio_chunked_path) if f[-4:] == '.wav' ]
    if os.path.exists(PATH_TO_CURRENT_CSV):
        dataset_csv = pd.read_csv(PATH_TO_CURRENT_CSV, error_bad_lines=False)
    else:
        dataset_csv = pd.DataFrame(
            columns=['wav_filename', 'wav_filesize', 'transcript', 'confidence_level'])
    #  now let's loop over this audio files
    for audio_name in audios_sanitized:
        r = sr.Recognizer()
        chunked_audio = sr.AudioFile(join_path(audio_chunked_path , audio_name))
        audio_file_size = os.stat(join_path(audio_chunked_path , audio_name)).st_size
        with chunked_audio as source:
            audio = r.record(source)
        audio_transcribe = ""
        # for confidence :
        #  -1 means google couldn't detect any speech.
        #  -2 means detected some but all are weak.
        #  -3 Error happend.
        #  [0, 1] means real probability.
        confidence = -1
        try:
            audio_transcribe = r.recognize_google(
                audio, language='fa-IR', show_all=True)

        except:
            audio_transcribe = "ERROR"
            confidence = -3
        finally:
            if len(audio_transcribe) > 0 and type(audio_transcribe) != str:
                if 'confidence' in audio_transcribe['alternative'][0]:
                    confidence = audio_transcribe['alternative'][0]['confidence']
                else:
                    confidence = -2
                new_row = {'wav_filename': audio_name, 'wav_filesize': audio_file_size,
                           'transcript': audio_transcribe['alternative'][0]['transcript'],
                           'confidence_level': confidence}
            else:
                new_row = {'wav_filename': audio_name, 'wav_filesize': audio_file_size,
                           'transcript': 'Google_Detected_No_Speech',
                           'confidence_level': confidence}

            # # append row to the dataframe
            dataset_csv = dataset_csv.append(
                new_row, ignore_index=True)
            dataset_csv.sort_values(by=['wav_filename'],inplace=True)
            dataset_csv.to_csv(PATH_TO_CURRENT_CSV, index=False)
    return dataset_csv



def track_name2text_name(track_name):
    '''
    

    Parameters
    ----------
    track_name : str or int
        Name of track.

    Returns
    -------
    str
        Name of corresponding text file for track_name.

    '''
    track_name=int(track_name)
    if track_name<100:
        if track_name <10:
            return f'output-00{track_name}.txt'
        else:
            return f'output-0{track_name}.txt'            
    else:
        return f'output-{track_name}.txt'
    
def is_fa(char):
    chars = 'ابپتثجچحخدذرزسشصضطظغعفقکگلمنوهی '
    if char in chars:
        return  True
    else:
        return  False
    
    
def clean_text(line):
    line=str(line)
    line = line.replace("‌"," ")
    line = re.sub(r"(\d+)", lambda x: convert(int(x.group(0))), line)
    line = ''.join(filter(is_fa, line))
    line=line.strip()
    # Add Hazm Normalize from Hazm to this function in order to better result in Levingeshtein
    normalizer = hazm.Normalizer() # persian_numbers , perisan_style= True : in order to uniformize text
    line=normalizer.normalize(line)
    return line


# Create output folder and check prerequisites
check_preq_files()
create_output_folder(output_dir)                
                

# Create speech range for raw speechs
audio_segment(audios_dir,csv_dir)


#Split raw audio

audio_files_dir=glob(join_path(audios_dir,'*.mp3'))
for audio_dir,i in zip(audio_files_dir,progressbar.progressbar(range(len(audio_files_dir)))):
    track_name=track_name_extractor(audio_dir)
    audio_split(audio_dir,join_path(csv_dir,track_name+'.csv'))
    


#Transcribe chunked audio
path_to_splitted=join_path(output_dir,'Output','Splitted')
splitted_dir=[join_path(path_to_splitted,f) for f in os.listdir(path_to_splitted) if os.path.isdir(join_path(path_to_splitted,f))]

for splitted,i in zip(splitted_dir,progressbar.progressbar(range(len(splitted_dir)))):
    transcribe_audios(splitted)
    
#Rename and create Final Audio file
path_to_text=join_path(project_dir,'text')

with open(join_path(project_dir,'error_list.txt'),'r') as fp:
    error_list=fp.readlines()
    error_list=list(map(lambda x:x.strip(),error_list))

meta_list=[]
meta_set=set() # Set in order to avoid have duplicate lines in metadata.csv
meta_error=open(join_path(output_dir,'Output','metadata_error.txt'),'w')

track_names=list(map(track_name_extractor,splitted_dir))   
for track_name in track_names:
    path_to_current_track=join_path(path_to_splitted,str(track_name))
    path_to_current_csv=join_path(output_dir,'Output','Transcript',f'{track_name}.csv')
    path_to_current_text=join_path(path_to_text,track_name2text_name(track_name))
    meta_error.write(f'{track_name}:\n')
    text=dict()
    with open(path_to_current_text,'r') as fp:
        for line in fp:
            line=line.split('|')
            text[int(line[0][2:])]=line[1]
    
    transcribe=pd.read_csv(path_to_current_csv)
    log=open(join_path(path_to_current_track,f'log_{track_name}.txt'),'w')
    for index,row in transcribe.iterrows():
        file_name=row['wav_filename']
        file_name=int(file_name[:file_name.find('.')])
        transcript=row['transcript']
        
        for key in list(text.keys()):
            if str(key) in error_list: #Unspoken
                log.write(f'{key}|Unspoken\n')
                del text[key]
                
        
        for sent_name in text:
            levensh=Levenshtein.ratio(clean_text(transcript),clean_text(text[sent_name]))
            
            if  levensh >= 0.9:
                
                copyfile(join_path(path_to_current_track,str(file_name)+'.wav'),join_path(output_dir,'Output','wavs',str(sent_name)+'.wav'))
                log.write(f'{sent_name}|Successful|{file_name} Copied with name {sent_name}\n')
                meta_line=f'{sent_name}|{text[sent_name]}'
                if meta_line not in meta_set: # In order to avoid duplicate in metedata.csv
                    meta_list.append(meta_line)
                    meta_set.add(meta_line)
            elif levensh >= 0.5:
                meta_error.write(f'Levenshtein Ratio:{levensh}\tSentence: {sent_name}|Track Name: {file_name}\n{text[sent_name]}|{transcript}\n')

                    
    meta_error.write('\n\n')
    log.close()

meta_error.close()
# Sort lines in meta_list according to their track name and insert in metadata.csv
meta_list=sorted(meta_list,key=lambda x:int(x.split('|')[0]))
with open(join_path(output_dir,'Output','metadata.csv'),'w') as meta:
    for line in meta_list:
        meta.write(line)
    
