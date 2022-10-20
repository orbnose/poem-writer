from db.config import configureDjango
import hashlib
import os
import shutil
import spacy
import re
import inflect
from nltk.stem.wordnet import WordNetLemmatizer

from casetense import NounTransformer

def get_book_string(path):
	READSIZE = 65536*5
	with open(path, mode='r', encoding="utf-8") as file:
		return file.read(READSIZE)

def get_hash(path):
	BLOCKSIZE = 65536
	with open(path, mode='r', encoding="utf-8") as file:
		read_string = file.read(BLOCKSIZE)
	return hashlib.md5(read_string.encode()).hexdigest()

def clean(text):

	# remove newline characters
	text = re.sub('\n', ' ', str(text))
	# remove apostraphes
	text = re.sub('\'', '', str(text))
	# remove hyphens and underscores
	text = re.sub('\-', ' ', str(text))
	text = re.sub('\_', ' ', str(text))
	# remove quotation marks
	text = re.sub('\"', '', str(text))
	# Replace ending punctuation
	text = re.sub('\!', '.', str(text))
	text = re.sub('\?', '.', str(text))
	text = re.sub('\:', '.', str(text))

	return text

class WordCleaner(inflect.engine):
	
	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)

		#define the conjugator
		self.verb_base = WordNetLemmatizer()
		self.noun_transformer = NounTransformer()

	def clean_word(self, text, pos_tag, dependency_label):
	# Transformations on text to get consistent letter casing, noun number, and verb number/tense in the database.
	#  Assumes english part of speech tagging provided by spacy.


		# Convert the text to lowercase if not a proper noun
		if not (pos_tag == 'NNP' or pos_tag == 'NNPS'):
			text = text.lower()
		
		#Handle nouns and pronouns
		if ('NN' in pos_tag or 'PRP' in pos_tag or 'WP' in pos_tag):
			return self.noun_transformer.transform(text, pos_tag, singular=True)
		
		# Convert verb to base form
		if 'VB' in pos_tag and not (
		 'nn' in dependency_label or 
		 'noun' in dependency_label or 
		 'np' in dependency_label or 
		 'nsub' in dependency_label or
		 'mod' in dependency_label or
		 'obj' in dependency_label or
		 'pcomp' in dependency_label or
		 'xcomp' in dependency_label):
			singular_verb = self.verb_base.lemmatize(text,'v')
			if singular_verb:
				text = singular_verb
			''' I tried using mlconjug3 via the line below, but it doesn't handle non-base verbs well
			     singular_verb = self.conjugator.conjugate(text).conjug_info['indicative']['indicative present']['3s']
			'''
		return text

def get_root_token(sentence_doc):
	for token in sentence_doc:
		if token.dep_ == 'ROOT':
			return token
	return None

def save_words_recur(root_token, ancestor_word_pk, Word, cleaner):
	
	# save root token
	text = root_token.text
	pos_tag = root_token.tag_
	dependency_label = root_token.dep_
	if dependency_label == "ROOT":
		dependency_label = 'root verb'

	# clean up text for database
	text = cleaner.clean_word(text, pos_tag, dependency_label)

	# TODO: Rewrite this
	_ = Word(text='Rewrite this...')
	word_pk = _.update_or_create_word(text, pos_tag, dependency_label, ancestor_word_pk)

	# process child tokens
	for child_token in root_token.children:
		save_words_recur(child_token, word_pk, Word, cleaner)


def save_words(sentence_doc, Word):
	cleaner = WordCleaner()
	
	root_token = get_root_token(sentence_doc)
	if not root_token:
		return None
	

	save_words_recur(root_token, ancestor_word_pk=None, Word=Word, cleaner=cleaner)


def main():
	from db.models import BookFile, Word

	nlp = spacy.load('en_core_web_sm')

	books_dir = 'books/'
	processed_dir = 'books/processed/'
	bookfiles = (file for file in os.listdir(books_dir)
				if os.path.isfile(os.path.join(books_dir, file)) )

	for bookfile in bookfiles :
		filepath = os.path.join(books_dir, bookfile)
		hash = get_hash(filepath)
		
		# Don't save books already processed
		if not BookFile.objects.filter(hash=hash):
			print("hash: " + hash)
			book = BookFile(filename=bookfile, hash=hash)
			book.save()
		
			# Open book file
			book_string = get_book_string(filepath)

			# Clean string
			book_string = clean(book_string)

			# Find sentences
			sentences = [str(sent) for sent in nlp(book_string).sents]

			# Get processing limits - assume the first and last 5% of the book are garbage
			num_sentences = len(sentences)
			if num_sentences > 5:
				lower_bound = int(num_sentences * 0.05)
				upper_bound = int(num_sentences * 0.95)
			else:
				lower_bound = 0
				upper_bound = num_sentences+1

			print("upper bound: ", upper_bound)
			print("lower bound: ", lower_bound)

			# Process sentences - assume all could be compound.
			for sentence in sentences[lower_bound:upper_bound]:

				# Ignore sentences with numerals
				if re.search(r'[0-9]+', sentence):
					continue

				sentence_doc = nlp(sentence)
				save_words(sentence_doc, Word=Word)

		# Move book into the books/processed/ directory
		shutil.move(filepath, processed_dir)




if __name__ == "__main__":
	configureDjango()
	main()
