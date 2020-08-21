# split_on_silence function for separating out silent chunks.
from pydub import AudioSegment
from pydub.silence import split_on_silence

# Define a function to normalize a chunk to a target amplitude.
def match_target_amplitude(aChunk, target_dBFS):
    ''' Normalize given audio chunk '''
    change_in_dBFS = target_dBFS - aChunk.dBFS
    return aChunk.apply_gain(change_in_dBFS)
def split(num, output_dir = "test/",ch_count=10):
    # Load your audio.
    try:
        song = AudioSegment.from_mp3(str(num) + ".mp3")
    except:
        pass
        # with open('fail.txt','a') as f:
        #     f.write("file {}:not found\n".format(num))
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
        silence_thresh = -33,
        keep_silence = 700
    )

    # Process each chunk with your parameters
    print(len(chunks))
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
                "./"+output_dir+"line_{0}.mp3".format(1+i+(num*10)),
                bitrate = "192k",
                format = "wav"
            )
    # else:
    # 	print(len(chunks))
    #     with open('fail.txt','a') as f:
    #         f.write("file {}:{}chunks\n".format(num,len(chunks)))
split(3,output_dir = "test/",ch_count=9)