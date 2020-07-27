# Text to Speech

In this repo i'm trying to cover the works I have done to train a persian text to speech model. this repo contains documents about the models i'm using to achive this goal as well as how to collect data for this task and the preprocesses that needs to be done on data.

## model
first step is to choose a model. after researching o n current suitable models, i decided to start with tacotron model. tacotron is an end to end model that has shown a great result and there has no crippling downsides. 
I  [This](https://github.com/keithito/tacotron) is the most used implementation for tacotron model. I used a [this fork](https://github.com/begeekmyfriend/tacotron) which is suggested by the main implementation. it has some of the benefits of tacotron 2 that reduces train time.

future work:
testing more models to see if there could be a better result.
suggested models for testing:
tacotron 2 
transformersTTS



## English dataset

before starting to collect persian data it was needed to test the model to see if i can get an acceptable result on english data. besides testing the model and getting familiar with it, testing with 
