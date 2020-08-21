# Import the AudioSegment class for processing audio and the 
# split_on_silence function for separating out silent chunks.
from pydub import AudioSegment
from pydub.silence import split_on_silence

# Define a function to normalize a chunk to a target amplitude.
def match_target_amplitude(aChunk, target_dBFS):
    ''' Normalize given audio chunk '''
    change_in_dBFS = target_dBFS - aChunk.dBFS
    return aChunk.apply_gain(change_in_dBFS)
def split(num, output_dir = "waves/",ch_count=10,nums=[i for i in range(1,11)]):
    # Load your audio.
    try:
        song = AudioSegment.from_mp3(str(num) + ".mp3")
    except:
        with open('fail.txt','a') as f:
            f.write("file {}:not found\n".format(num))
        return
    song = song[500:]
    # Split track where the silence is 2 seconds or more and get chunks using 
    # the imported function.
    # print(split_on_silence (song))
    chunks = split_on_silence (
        # Use the loaded audio.
        song, 
        # Specify that a silent chunk must be at least 2 seconds or 2000 ms long.
        min_silence_len = 1500,
        # Consider a chunk silent if it's quieter than -16 dBFS.
        # (You may want to adjust this parameter.)
        silence_thresh = -33 ,
        keep_silence = 700
    )

    # Process each chunk with your parameters
    if len(chunks)==ch_count:
        print("exporting file {}.mp3".format(num))
        for i, chunk in enumerate(chunks):
            # Create a silence chunk that's 0.5 seconds (or 500 ms) long for padding.
            # silence_chunk = AudioSegment.silent(duration=500)

            # Add the padding chunk to beginning and end of the entire chunk.
            # audio_chunk = silence_chunk + chunk + silence_chunk
            audio_chunk = chunk

            # Normalize the entire chunk.
            normalized_chunk = match_target_amplitude(audio_chunk, -20.0)

            # Export the audio chunk with new bitrate.
            # print("Exporting chunk{0}.mp3.".format(1+i+(num*10)))
            normalized_chunk.export(
                "./"+output_dir+"line_{0}.mp3".format(nums[i]+(num*10)),
                bitrate = "192k",
                format = "wav"
            )
    else:
        with open('fail.txt','a') as f:
            f.write("file {}:{}chunks\n".format(num,len(chunks)))
# files = []
# with open("fail2.txt",'r') as f:
#     for line in f:
#         files.append(line.split(':')[0].strip("file "))
# for i in files:
#     split(int(i))
miss = set()
with open('mistakes.txt', 'r') as m:
    for line in m:
        miss.add(int(line))
for i in range(1,360):
    file_ch_c = 10
    number_list = [n for n in range(1,11)]
    for j in range (1,11):
        if (i*10)+ j in miss:
            print('miss:{}'.format((i*10)+ j))
            number_list.remove(j)
            file_ch_c -= 1
    split(int(i),ch_count=file_ch_c,nums=number_list)