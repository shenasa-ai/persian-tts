
"""
What this code do ? 
    Find Heteronyms word in your corpus with help of Vajehyab API
* This code have capability to resume from last run. it saved json file downloaded from Vajehyab and detect them in next run and don't download them again.
@author: anvaari
"""

# Import required packages
from glob import glob
from parsivar import SpellCheck
from parsivar import Normalizer
from parsivar import Tokenizer
from parsivar import FindStems
import os
from os.path import join as join_path
import argparse
import requests
import json
import progressbar
from pprint import pprint
import pickle

# Path to where script exist
script_path=os.path.abspath(os.path.dirname(__file__))

# Set up argparse
parser = argparse.ArgumentParser(description='Find Heteronyms word in your corpus with help of Vajehyab API')
    
parser.add_argument(
"--corpus-path",
dest='text_path',
type=str,
help="Path to where our corpus exist (must in .txt format)",
)
                            

parser.add_argument(
"--token",
dest='token',
type=str,
help="Token of your Vajehyab developer account",
)

parser.add_argument(
"--output",
dest='output_path',
type=str,
default=script_path,
help="Path to output folder. If you already have some word.json files and want to resume progress set this to folder where words_json folder exist. [Optional, default is code's directory]",
)

args = parser.parse_args()

output_path=args.output_path
text_path=args.text_path
token=args.token

 


def get_unique_words(text_path):
    '''
    This function get text corpus path as input and give set of unique words as output.

    Parameters
    ----------
    text_path : str
        Path to where our corpus exist (must in .txt format).

    Raises If spell check package of parsivar won't found.'
    ------
    
    Returns
    -------
    words_set : set
        Set of unique words from corpus.

    '''
    # Create a list from all text
    text_names=glob(join_path(text_path,'*.txt'))
    sentences=[]
    for name in text_names:
        with open(name,'r') as text:
            text_sentences=tuple(text.readlines())
        for sentence in text_sentences:
            sentence=sentence.strip('\n')
            sentences.append(sentence[sentence.find('|')+1:])
    
    # Specify Signs and Numbers in order to avoid words contain them enter in our final Set 
    signs=['،','«','»','.',')','(','"',':',';','%','-','?',',','؛',"'",'_']
    numbers=[f'{i}' for i in range(10)]
    
    
            
    # Create Set of all words in corpus
    try:
        spell=SpellCheck()
    except:
        raise Exception('Please download spell.zip from https://www.dropbox.com/s/tlyvnzv1ha9y1kl/spell.zip?dl=0 and extract to path to parsivar/resource.')
    normal=Normalizer()
    token=Tokenizer()
    stemm=FindStems()
    words_set=set()
    print('\n Start to extract and clean words from sentences! \n')
    with progressbar.ProgressBar(max_value=len(sentences),redirect_stdout=True) as bar:
        for sentence,i in zip(sentences,range(len(sentences))):
            sentence=normal.normalize(spell.spell_corrector(sentence))
            sentence=sentence.replace(u'\u200c',' ')
            words=token.tokenize_words(sentence)
            for word in words:
                word=stemm.convert_to_stem(word)
                if '&' in word: #This pattern found manually in text
                    word=word[:word.find('&')]
                if word in signs : # Ignore signs
                    bar.update(i)
                    continue
                for let in word: # Ignore words contain numbers
                    if let in numbers:
                        bar.update(i)
                        continue
                if len(word) <=1: # ignore one (or less)letter strings
                    bar.update(i)                    
                    continue
                words_set.add(word) 
                bar.update(i)
    return words_set


def send_request_amid(word,token):
    '''
    Function to send word to Vajehyab API (Amid dictionary)


    Parameters
    ----------
    word : str
        Word you want to send to vajehyab.
    token : str
        Token from your developer account.

    Returns
    -------
    status_code : int
        You can read more here : https://www.vajehyab.com/api/documentation .
    content : bytes
        content recieved from Vajehyab.

    '''
    try:
        response = requests.get(
            url="http://api.vajehyab.com/v3/search",
            params={
                "token": f"{token}",
                "q": word,
                "type": "exact",
                "filter": "amid",
            },
        )
        content=response.content
        status_code=response.status_code
        return status_code,content
    except requests.exceptions.RequestException:
        print('HTTP Request failed')
        
def words_amid_info(words_set,output_path,token):
    '''
    

    Parameters
    ----------
    words_set : set
        set of preproccessed words of our corpus.
    output_path : str
        Path to output folder.
    token : str
        Token of Vajehyab API.

    Returns
    -------
    words0 : list
        words which amid dictionary don't support, so it return no value for them.
    words_fail : list
        list of word server fail to handle their request.

    
    ------
    Function also create pickle file include words0 and words_fail
    '''
    # Create words_json folder in output_path in order to save word's json files
    words_path=join_path(output_path,'words_json')
    if not os.path.isdir(words_path):
        os.mkdir(words_path)
        

    # Load words already gathered and saved in order to spend less mony for api :)
    word_done_file=os.listdir(words_path)
    word_done=[]
    for word in word_done_file:
        word_done.append(word[:word.find('.')])
    # Load words0 and words_fail if exist. This piece add reume capability.
    fail_pickle_path=join_path(output_path,'words_faile_pickle')
    if os.path.isfile(fail_pickle_path):
        with open(fail_pickle_path,'rb') as fp:
            words0,words_fail=pickle.load(fp)
    else:
        words0=[]
        words_fail=[]
    # Send word through send_request_amid function and handle different situation
    print('\n Start sending words to Vajehyab (Amid Dictionary) \n')
    with progressbar.ProgressBar(max_value=len(words_set),redirect_stdout=True) as bar:
        for word,i in zip(words_set,range(len(words_set))):
            if word in word_done or word in words0:
                bar.update(i)
                continue
            respond=send_request_amid(word,token)
            if respond[0]!=200:
                words_fail.append(word)
                bar.update(i)
                continue  
            content=json.loads(respond[1])
            if content.get('debug'):
                if content.get('debug').get('message')=='توکن نامعتبر است.':
                    raise Exception('Your token is invalid')
        
            if content['data']['num_found']==0:
                words0.append(word)
            else:
                with open(join_path(words_path,f'{word}.json'),'w') as fp:
                    json.dump(content,fp)
            bar.update(i)
    # Save words0 and words_fail. This piece add reume capability.              
    with open(fail_pickle_path,'wb') as fp:
        pickle.dump([words0,words_fail], fp)
        
    return words0,words_fail
    

def amid2heteronym(output_path):
    '''
    

    Parameters
    ----------
    output_path : str
        Path to where you want place output folder.

    Returns
    -------
    heteronym : dict
        Dictionary which its keys are words and their value are dictionary which contain different way this word pronounce and their meaning.

    '''
    word_pron_mean_dict=dict() # Keys are all words, which their information successfully received from Vajehyab. Values are different pronunciations of words with their meanings.
    jsons_path=glob(join_path(output_path,'words_json','*.json'))
    
    
    for json_path in jsons_path:
        with open(json_path) as fp:
            word_data=json.load(fp)
        word_name=json_path[json_path.rfind('/')+1:json_path.rfind('.')]
        word_pron_mean_dict[word_name]=dict()
        for num in range(word_data['data']['num_found']):
            pron=word_data['data']['results'][num]['pron']
            pron=pron.replace("&#39;","'")
            mean=word_data['data']['results'][num]['text']
            if pron in word_pron_mean_dict[word_name]:
                word_pron_mean_dict[word_name][pron].append(mean)
            else:
                word_pron_mean_dict[word_name][pron]=[mean]
    # Create heteronym dict contain heteronym words and their different pronunciations and meanings.
    heteronym=dict()
    
    for word in word_pron_mean_dict:
        if len(word_pron_mean_dict[word])>1:
            heteronym[word]=word_pron_mean_dict[word]
         
    with open(join_path(output_path,'heteronyms.json'),'w') as fp:
        json.dump(heteronym, fp)            
    return heteronym


if __name__=='__main__':
    if not output_path:
        output_path=input('\nPlease enter output_path. If you enter invalid directory or press enter, path to this code will be select as output_path\nIf you already have some word.json file and want to resume progress set this to folder where words_json folder exist.\n')
        if not os.path.isdir(output_path):
            output_path=script_path
            
    if not text_path:
        text_path=''
        while not os.path.isdir(text_path):
            text_path=input('\nPlease enter text_path. It must be specified. You should type valid directory\n')
    
    while not token:
        token=input('\nPlease enter your Vajehyab token. It must be specified\n')
        
    unique_words=get_unique_words(text_path)
    fail_0,fail=words_amid_info(unique_words, output_path, token)
    heteronyms=amid2heteronym(output_path)
    print(f"\nAmid dictionary don't support these words :\n{fail_0}\n")
    print(f"\nVajehyab cant handle these words :\n{fail}\n")
    if len(heteronyms)<50:
        print('\nHeteronym words with its meanings:\n')
        pprint(heteronyms)
    else:
        print('Heteronyms save in heteronyms.json in output folder')
    

        
        
    
