import re
from fa import convert
line_count = 0
line_lens = []

files_count = 36

for i in range(1,files_count):
    with open(str(i)+".txt", 'r',encoding='utf-8') as read_file:
        lines = read_file.readlines()
    with open(str(i)+"-p.txt", "w",encoding='utf-8') as save_data:
        for line in lines:
            line = line.replace(";", ".\n")
            line = line.replace(":", ".\n")
            line = line.replace("؛", ".\n")
            line = line.replace(".", ".\n")
            line = line.replace("؟", "؟\n")
            line = line.replace("?", "؟\n")
            line = line.replace("%", "درصد")
            line = line.replace("٪", "درصد")
            bad_chars = ['«','»','َ','ُ','ِ','ّ','ْ','ٔ','…','“','”','"','*',']','['] 
            for j in bad_chars : 
                line = line.replace(j, '') 

            save_data.write(line)
    # remove unfixable lines
    with open(str(i)+"-p.txt", "r",encoding='utf-8') as f_input:
        lines = f_input.readlines()
    line_count+= len(lines)    
    with open(str(i)+"-p.txt", "w",encoding='utf-8') as save_data:
        regexp = re.compile(r'[a-zA-Z|/Ñ♦+#]')
        last_line = ''
        for line in lines:
            if len(line)<10 or len(line)> 200 or line == last_line:
                continue
            if len(line)> 190:
                print("file:"+str(i))
            if not regexp.search(line):
                last_line = line
                save_data.write(line)
                line_lens.append(len(line))

    with open("ch-set.txt", "r",encoding='utf-8') as f_input:
        chset = f_input.read()
    with open(str(i)+"-p.txt", "r",encoding='utf-8') as f_input:
        text = f_input.read()
    text = re.sub(r"(\d+)", lambda x: convert(int(x.group(0))), text)
    chset="".join(sorted(''.join(set(text+chset))))

    with open(str(i)+'-pn.txt', 'w',encoding='utf-8') as f_output:
        f_output.write(text)

    with open('ch-set.txt', 'w',encoding='utf-8') as f_output:
        f_output.write(chset)
final = open("output-0000.txt", 'w',encoding='utf-8')
j=1
for i in range(1,files_count):
    with open(str(i)+'-pn.txt', 'r',encoding='utf-8') as f_input:
        lines = f_input.readlines()
    for line in lines:
        final.write('خط'+(4-len(str(j)))*'0'+str(j)+'|'+line)
        if j%10 ==0:
            final.close()
            final = open("output-"+(3-len(str(j//10)))*'0'+str(j//10)+".txt", 'w',encoding='utf-8')
        j+=1
final.close()
with open('line-lens.txt', 'w',encoding='utf-8') as f_output:
        f_output.write(str(line_lens))
        print(max(line_lens))

print(line_count)

# distribution
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import matplotlib.mlab as mlab

num_bins = 20

n, bins, patches = plt.hist(line_lens, num_bins, facecolor='blue', alpha=0.5)
samples = np.random.normal(np.mean(line_lens), np.std(line_lens), size=len(line_lens))
n, bins, patches = plt.hist(samples, num_bins, facecolor='red', alpha=0.5)
plt.show()

# def ecdf(data):
#     """Compute ECDF for a one-dimensional array of measurements."""

#     # Number of data points: n
#     n = len(data)

#     # x-data for the ECDF: x
#     x = np.sort(data)

#     # y-data for the ECDF: y
#     y = np.arange(1, n+1) / n

#     return x, y
# x, y = ecdf(line_lens)

# plt.figure(figsize=(8,7))
# sns.set()
# plt.plot(x, y, marker=".", linestyle="none")
# plt.xlabel("Body Temperature (F)")
# plt.ylabel("Cumulative Distribution Function")

# samples = np.random.normal(np.mean(line_lens), np.std(line_lens), size=10000)
# x_theor, y_theor = ecdf(samples)
# plt.plot(x_theor, y_theor)
# plt.legend(('Normal Distribution', 'Empirical Data'), loc='lower right')
# plt.show()