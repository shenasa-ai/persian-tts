'''
add 100 to mp3 file names (1->259) to match the txt files.
all the first 100 mp3 files and this script should be in a directory
cuurent directory must contain an empty directory named mapped.
processed files are copied to mapped directory.
if it can't find a sound file writes its number to "na.txt".
'''
from shutil import copyfile
with open('na.txt','w') as f:	
	for i in range(1,260):
		try:
			copyfile('{}.mp3'.format(i),'./mapped/{}.mp3'.format(i+100))
		except:
			f.write(str(i+100)+'\n')


'''
change mp3 file names to match txt files using "map.txt" file.
"map.txt" should exist in current directory.
'''
tuple_list = []
with open('map.txt','r') as f:
	for line in f:
		tup = line.split('\t')
		if tup[1]!='\n':
			m = int(tup[0])
			n = int(tup[1])
			copyfile('ضبط_بدون_عنوان({}).mp3'.format(m), './mapped/{}.mp3'.format(n))
print(tuple_list)
n= 422