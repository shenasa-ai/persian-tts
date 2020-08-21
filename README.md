# Text to Speech

In this repo i'm trying to cover the works I have done to train a persian text to speech model. this repo contains documents about the models i'm using to achive this goal as well as how to collect data for this task and the preprocesses that needs to be done on data.

## model
first step is to choose a model. after researching o n current suitable models, i decided to start with tacotron model. tacotron is an end to end model that has shown a great result and there has no crippling downsides. [This](https://github.com/keithito/tacotron) is the most used implementation for tacotron model. I used a [this fork](https://github.com/begeekmyfriend/tacotron) which is suggested by the main implementation. it has some of the benefits of tacotron 2 that reduces train time.

future work:
testing more models to see if there could be a better result.
suggested models for testing:
tacotron 2 
transformersTTS



## English dataset

before starting to collect persian data it was needed to test the model to see if i can get an acceptable result on english data. besides testing the model and getting familiar with it, testing with english data could provide us with some result that could be compared to the result from persian dataset to see if the result is not satisfying, we should fix the model or the dataset.
the english dataset that i decided to use is [LJSpeech](https://keithito.com/LJ-Speech-Dataset)
this dataset is compatible with most of the current models and they have preprocess codes and benchmarks ready for it.

## Creating dataset and preprocess tools
there is some guidelines for creating a dataset for TTS models. some of these guidelines should be followed by the voice actor. these points are gathered in [recording_guide.pdf](https://github.com/shenasa-ai/persian-tts/blob/master/recording_guide.pdf) which is present in this repo.
but before giving the task to voice actor you need to have a structured text curpus. the text file should be seperated by sentences. the lines should not be too short or too long and must not contain words from other languages. other than that, the numbers in text file should be written with alphabet chars.
the last step is to strip the text from unwanted chars and give each line a number.
this jobs can be done using the [parser.py](https://github.com/shenasa-ai/persian-tts/blob/master/parser.py) script. 
this script also plots the histogram of the sentense lengths distribution compared to the normal distribution. the similarity between these distributions is one of the parameters of a good data set.

 the voice actor required me to give him the text files in docx format so i wrote the [t2d.py](https://github.com/shenasa-ai/persian-tts/blob/master/t2d.py) script to convert the txt files to docx.
this sctipt converts all the txt files in current directory to docx format.

after gathering text, there are some statistical analysis that you may want to do on your text. I included the tools I made for that purpose in this repo.
first of these tools is the scipt to count occurance of a word in the text and sorting them. this can be done using [top-words.py](https://github.com/shenasa-ai/persian-tts/blob/master/top-words.py)
it analyses the final.txt file and outputs word_count.txt which contains the descendingly sorted list of all words used in final.txt with their occurance count.

after reciving the voice files, the file namings didnt match the naming of the text files. renaming the voice files was done using the [voice_text_matcher.py](https://github.com/shenasa-ai/persian-tts/blob/master/voice_text_matcher.py)
additional info is commented in the script itself.

the next step is to split the voice files into single line wav files. this task is done using the pydub lib and its split_on_silence function. the [split.py](https://github.com/shenasa-ai/persian-tts/blob/master/split.py) is the script to do this. this script splits each voice file of silence and if there is exactly 10 slices, it saves the output in /wavs; otherwise it logs faling into fail.txt . this script aslo supports having lines that may not exist in voice file. you just have to write line numbers in mistakes.txt ,seperated by new line and the script will expect the related voice file to miss that file. for having a clean cut you need to tune the silence_thresh variable. for testing the silence_thresh you can use [split-test.py]( https://github.com/shenasa-ai/persian-tts/blob/master/split-test.py) and after finding the desired threshold, you can run the main script.
