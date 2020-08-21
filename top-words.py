text = []
with open('final.txt', 'r', encoding='utf-8') as f:
	for line in f:
		text.append(line.split('|')[2])
word_dic = {}

for line in text:
	line_split = line.translate(str.maketrans('','','!(),-.[]_،؟!@#$\n')).split(' ')
	for word in line_split:
		if word in word_dic:
			word_dic[word] += 1
		else:
			word_dic[word] = 1
word_dic_sorted = {k: v for k, v in sorted(word_dic.items(), key=lambda item: item[1], reverse=True)}
with open('word_count.txt', 'w', encoding='utf-8') as w:
	for rank ,(word, count) in enumerate(word_dic_sorted.items()):
		w.write('{}-word: {}, count: {}\n'.format(rank+1, word, count))

