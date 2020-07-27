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

## Creating dataset
there is some guidelines for creating a dataset for TTS models. some of these guidelines should be followed by the voice actor. these points are gathered in recording_guide.pdf which is present in this repo.
but before giving the task to voice actor you need to have a structured text curpus. the text file should be seperated by sentences. the lines should not be too short or too long and must not contain words from other languages. other than that, the numbers in text file should be written with alphabet chars.
the last step is to strip the text from unwanted chars and give each line a number.
this jobs can be done using the parser.py script. 
this script also plots the histogram of the sentense lengths distribution compared to the normal distribution. the similarity between these distributions is one of the parameters of a good data set.

 the voice actor required me to give him the text files in docx format so i wrote the t2d.py script to convert the txt files to docx.
this sctipt converts all the txt files in current directory to docx format.
