import hashlib
import os
import shutil
import spacy
import re
from .models import BookFile, Template, update_or_create_word
import time

from .casetense import NounTransformer, VerbTransformer

def print_elapsed_time(start, end):
	# Assuming inputs from time.time() in seconds
	total_seconds = end - start
	hours = int(total_seconds / 3600)
	seconds_leftover = total_seconds - hours*3600
	minutes = int( seconds_leftover / 60 )
	seconds = seconds_leftover - minutes*60
	print(f"Elapsed time: {hours}:{minutes}:{seconds}")

def get_book_string(path):
	READSIZE = 65536*5
	with open(path, mode='r', encoding="utf-8") as file:
		return file.read(READSIZE)

def get_book_hash(path):
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

def is_verb_position(pos_tag, dependency_label):
	if 'VB' in pos_tag and not (
		 'nn' in dependency_label or 
		 'noun' in dependency_label or 
		 'np' in dependency_label or 
		 'nsub' in dependency_label or
		 'mod' in dependency_label or
		 'obj' in dependency_label or
		 'pcomp' in dependency_label or
		 'xcomp' in dependency_label):
		return True
	return False

class WordCleaner():
	
	def __init__(self, *args, **kwargs):

		#define the transformers
		self.verb_transformer = VerbTransformer()
		self.noun_transformer = NounTransformer()

	def clean_word(self, text, pos_tag, dependency_label):
	# Transformations on text to get consistent letter casing, noun number, and verb number/tense in the database.
	#  Assumes english part of speech tagging provided by spacy.
		
		# Convert nouns and pronouns to singular form
		if ('NN' in pos_tag or 'PRP' in pos_tag or 'WP' in pos_tag):
			return self.noun_transformer.transform_for_db(text, pos_tag, dependency_label)
		
		# Convert verbs to base form (lemma)
		if is_verb_position(pos_tag, dependency_label):
			return self.verb_transformer.transform_for_db(text)
		
		# Otherwise, just lowercase it
		return text.lower()

def get_root_token(sentence_doc):
	for token in sentence_doc:
		if token.dep_ == 'ROOT':
			return token
	return None

def save_words_recur(root_token, ancestor_word_pk):
	
	# save root token
	text = root_token.text
	pos_tag = root_token.tag_
	dependency_label = root_token.dep_

	# clean up text for database
	text = word_cleaner.clean_word(text, pos_tag, dependency_label)

	# Save or update word
	word_pk = update_or_create_word(text, pos_tag, dependency_label, ancestor_word_pk)

	# process child tokens recursively
	for child_token in root_token.children:
		save_words_recur(child_token, word_pk)

def extract_template_features(sentence_doc):
	pos_tags_list = []
	dependency_labels_list = []
	dependency_order_list = []
	is_root_verb = False
	is_root_imperative = True
	num_words = len(sentence_doc)

	for token in sentence_doc:
		pos_tags_list.append(token.tag_)
		dependency_labels_list.append(token.dep_)
		dependency_order_list.append( len(list(token.ancestors)) )
		if token.dep_ == 'ROOT' and is_verb_position(token.tag_, token.dep_):
			is_root_verb = True
		if token.dep_ == 'expl' or 'sub' in token.dep_:
			is_root_imperative = False

	template = Template(is_root_verb=is_root_verb, is_root_imperative=is_root_imperative, num_words=num_words)
	template.set_pos_tags(pos_tags_list)
	template.set_dependency_labels(dependency_labels_list)
	template.set_dependency_order(dependency_order_list)
	template.set_hash()

	if not Template.objects.filter(hash=template.hash): #already exists
		template.save()
	else:
		template = None

def save_words_and_template(sentence):
	
	# Ignore sentences with numerals
	if re.search(r'[0-9]+', sentence):
		return None

	# Tag the sentence
	sentence_doc = nlp(sentence)

	# Save words
	root_token = get_root_token(sentence_doc)
	if not root_token:
		return None
	save_words_recur(root_token, ancestor_word_pk=None)

	# Extract template features and save if unique
	template = extract_template_features(sentence_doc)

# --- #--- # --- #--- # --- #--- Module-wide tools ---# ---# ---# ---# ---# ---#
nlp = spacy.load('en_core_web_sm')
word_cleaner = WordCleaner()
# --- #--- # --- #--- # --- #---  Main function ---# ---# ---# ---# ---# ---#
def extract_books(books_dir):

	# Set up tools and directories
	starttime = time.time()
	processed_dir = os.path.join(books_dir, 'processed/') #'books/processed/'
	bookfiles = (file for file in os.listdir(books_dir)
				if os.path.isfile(os.path.join(books_dir, file)) )

	# Process book files
	for bookfile in bookfiles:
		filepath = os.path.join(books_dir, bookfile)
		hash = get_book_hash(filepath)
		
		# Don't save books already processed
		if not BookFile.objects.filter(hash=hash):
			book = BookFile(filename=bookfile, hash=hash)
			book.save()
			print("Processing ", bookfile, "...")

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

			# Process sentences
			sent_num = 0
			total_sent = upper_bound - lower_bound
			for sentence in sentences[lower_bound:upper_bound]:
				
				# here's where the magic happens...
				save_words_and_template(sentence)		

				
				# Display ongoing count
				sent_num = sent_num + 1
				print('Progess: (', sent_num,'/', total_sent,') complete...', end='\r', flush=True)

				'''
				# Display dots every 100 sentences
				
				if sent_num%100==0:
					print('.', end=" ", flush=True)
				'''

		# Move book into the books/processed/ directory
		shutil.move(filepath, processed_dir)

		#print elapse time
		endtime = time.time()
		print('\n')
		print_elapsed_time(starttime, endtime)