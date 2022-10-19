from db.config import configureDjango
import spacy
import random

def main():
    from db.models import Word
    nlp = spacy.load('en_core_web_sm')

    template_text = "I eat dirt. I digest. My body learns to protect against the swallowed microbes. I paradoxically improve by eating garbage."
    template_doc = nlp(template_text)
    template = []
    sentence = []

    # build template
    for token in template_doc:
        label = str(token.dep_)
        if label == "ROOT":
            label = 'root verb'
        template.append( label )
    
    # look up words
    for label in template:
        if label == 'punct':
            sentence.append('.')
        else:
            wordlist = Word.objects.filter(dependency_label=label)
            max = len(wordlist)
            word = wordlist[ random.randrange(0, max) ]
            sentence.append(word.text)
    
    # print sentence

    sentence_text = ""
    for text in sentence:
       sentence_text = sentence_text + text + " "
    print(sentence_text, '\n')
    print(str(template))

if __name__ == "__main__":
	configureDjango()
	main()