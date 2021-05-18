# Text to Speech

In this repo I'm trying to cover the works I have done to train a Persian text to speech model. This repo contains documents about the models I'm using to achieve this goal as well as how to collect data For this task and the preprocesses that need to be done on data.

## Model
First step is to choose a model. After researching current suitable models, I decided to start with tacotron model. Tacotron is an end to end model that has shown a great result and there have no crippling downsides. [This](https://github.com/keithito/tacotron) is the most used implementation for tacotron model. I used a [this fork](https://github.com/begeekmyfriend/tacotron) which is suggested by the main implementation. It has some of the benefits of tacotron 2 that reduces train time.

**Future work:**
* Testing more models to see if there could be a better result.

**Suggested models for testing:**
* tacotron 2 
* transformersTTS



## English dataset

Before starting to collect Persian data it was needed to test the model to see if I can get an acceptable result on English data. Besides testing the model and getting familiar with it, testing with English data could provide us with some results that could be compared to the result from Persian dataset to see if the result is not satisfying, we should fix the model or the dataset.
The English dataset that I decided to use is [LJSpeech](https://keithito.com/LJ-Speech-Dataset)
This dataset is compatible with most of the current models and they have preprocess codes and benchmarks ready for it.

## Creating dataset and preprocess tools
There are some guidelines for creating a dataset for TTS models. Some of these guidelines should be followed by the voice actor. These points are gathered in [recording_guide.pdf](https://github.com/shenasa-ai/persian-tts/blob/master/recording_guide.pdf) which is present in this repo.
But before giving the task to a voice actor you need to have a structured text corpus. The text file should be separated by sentences. The lines should not be too short or too long and must not contain words from other languages. Other than that, the numbers in text file should be written with alphabet chars.
The last step is to strip the text from unwanted chars and give each line a number.
These jobs can be done using the [parser.py](https://github.com/shenasa-ai/persian-tts/blob/master/parser.py) script. 
This script also plots the histogram of the sentence length distribution compared to the normal distribution. The similarity between these distributions is one of the parameters of a good data set.

### TXT to Docx
The voice actor required me to give him the text files in docx format so I wrote the [t2d.py](https://github.com/shenasa-ai/persian-tts/blob/master/t2d.py) script to convert the txt files to docx.
This script converts all the txt files in the current directory to docx format.

### Statistical Analysis On Text
After gathering text, there is some statistical analysis that you may want to do on your text. I included the tools I made for that purpose in this repo.
The first tool is the script to count the occurrence of a word in the text and sorting them. This can be done using [top-words.py](https://github.com/shenasa-ai/persian-tts/blob/master/top-words.py)
It analyses the final.txt file and outputs word_count.txt which contains the descendingly sorted list of all words used in final.txt with their occurrence count.

### Process and validate voices after receiving from voice actor

#### Match voice file names and text files
After receiving the voice files, the file namings didn't match the naming of the text files. Renaming the voice files was done using the [voice_text_matcher.py](https://github.com/shenasa-ai/persian-tts/blob/master/voice_text_matcher.py)
Additional info is commented in the script itself.

#### Split voices 


There are text files from which audio files have been made, in these audio files the voice actor has made several mistakes, for example, the actor miss reads a sentence or fails to read and starts that sentence from the top or jumps over a sentence. Each audio file should correspond to a text file with 10 lines but as explained above there are some errors.

So our task is to :
1. Split voice files when the actor begins to read and continue until the actor is finished (Split by silence).
3. Validate voices with text, to have valid splitted voices (each splitted voice must correspond to one line of each text).
4. Create `metadata.csv`. There should be one valid voice for each line in `metadata.csv`.

**For task 1:** We use [inaSpeechSegmenter](https://github.com/ina-foss/inaSpeechSegmenter) which is a CNN-based audio segmentation toolkit. Allows to detect speech, music and speaker gender. It is smarter than pydub and other silence detectors and separates speech and silence precisely. And also we use [pydub](https://github.com/jiaaro/pydub) to split voices using intervals created by inaSpeechSegmenter.

**For task 2:** We use [this speech recognition](https://github.com/Uberi/speech_recognition) tool to transcript our voices. Also, we calculate the similarity of transcript and text using [Levenshtein](https://github.com/ztane/python-Levenshtein/) method. Then for 10 (or fewer) voices splitted (which correspond to one text file), voice transcripts and text lines compared and if the similarity score is more than 0.9, the result is valid.

**For task 3:** for each voice marked as valid add it's correspond line to the metedata.csv
**All this tasks done in [splitter.py](https://github.com/shenasa-ai/persian-tts/blob/master/splitter.py)**
##### How to use:
**Clone** the repository : 
``` bash
git clone https://github.com/shenasa-ai/persian-tts.git
cd persian-tts
```

**Prerequisites**:
It is better to create a virtual environment :
``` bash
python -m venv venv
``` 
Activate it and update pip:
``` bash 
source venv/bin/activate
pip install --upgrade pip
```
Then install all prerequisite packages using pip : 
``` bash 
pip install -r splitter_requirements.txt
```
The directory contains `splitter.py` must contain some file and folder as below:
``` 
.
├── splitter.py
├── fa.py
├── error_list.txt          # Contain lines that the voice actor didn't read
└──text
    ├── output-000.txt
    ├── output-001.txt
    ├── output-002.txt
    ...
```


**Usage:**
``` bash
python splitter.py -h

```
Example:
``` bash
python splitter.py --audio-dir 'path/to/audios/folder' --output-dir 'path/to/where/you/want/output/folder/create' --csv-dir 'path/to/folder/contain/csvs'
```
Args:
``` bash
--audio-dir           # Directory includes raw voices which aren't processed and split yet.
--csv-dir             # [Optional] Directory include processed CSVs from inaSpeechSegmenter. For purpose of Note 1. Default is output_folder/CSVs
--output-dir          # Directory which you want to place output folder there. Default is project folder
```


**Notes:** 
1. It takes much time for inaSpeechSegmenter to determine speech part and export it (and also for google speech recognition too), So I design this code so that if your PC turned off or something out of control happened, you'll be able to resume progress. So in the first step all files are saved on your storage and then process begin :).

2. inaSpeechSegmenter don't recognize and split silence at the beginning of the file and at the end of it so in the first and last splitted file (of each voice file) we have unnormal silence (greater than 500 milliseconds).

3. while inaSpeechSegmenter running it produces many warnings and logs in output like :
```
2021-05-18 15:37:11.725633: I tensorflow/compiler/jit/xla_cpu_device.cc:41] Not creating XLA devices, tf_xla_enable_xla_devices not set
2021-05-18 15:37:11.725860: I tensorflow/core/platform/cpu_feature_guard.cc:142] This TensorFlow binary is optimized with oneAPI Deep Neural Network Library (oneDNN) to use the following CPU instructions in performance-critical operations:  SSE4.1 SSE4.2 AVX AVX2 FMA
To enable them in other operations, rebuild TensorFlow with the appropriate compiler flags.
2021-05-18 15:37:11.726213: I tensorflow/core/common_runtime/process_util.cc:146] Creating new thread pool with default inter op setting: 2. Tune using inter_op_parallelism_threads for best performance.
```
Don't pay attention to them. 
**Output Folder**:
By default `output` folder create in project folder (where splitter.py exist) so:
```
├── splitter.py
├── fa.py
├── error_list.txt         
├──text
|   ├── output-000.txt
|   ├── output-001.txt
|   ├── output-002.txt
|    ...
└── output
     ├── metadata.csv       # Contain lines, each line begin with a number (number of line in our text correspond to voice file in wavs folder) then | and then sentence. metadata.csv contains all sentences whose corresponding voices are valid and exist in wavs folder.
     ├── metadata_error.txt # Contain errors (for debugging)
     ├── Splitted           # Contain Folders, each folder corresponds to one text file (naming are same). Also, folders contain splitted voices (voices after split using inaSpeechsegmenter and pydub save here)
     ├── Transcript         # Contain CSV files, each of them corresponds to one voice file (naming are same). Also, CSVs contain a transcript of splitted voices.
     ├── wavs               # Contain all valid voices. The name of the files are set according to their corresponding sentence number
     ├── CSVs               # Contain CSVs. Each CSV is the output of inaSpeechSegmenter and contains intervals that the voice actor speaks.

```
**So:**
* **`metedata.csv` and `wavs` are our final output**
* **`splitted`, `Transcript` and `CSVs` (if exist) contain data, saved during processing**
* **`metadata_error.txt` is for debugging purpose**
