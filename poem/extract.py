from ast import Pass
from codecs import replace_errors
import hashlib
import os
from pickle import NONE
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
	text = re.sub(r'\-', ' ', str(text))
	text = re.sub(r'\_', ' ', str(text))
	# convert semicolons
	text = re.sub(r';', ',', str(text))

	# turn quotes and brackets into sentences
	text = re.sub(r'\"', '.', str(text))
	text = re.sub(r'`', '.', str(text))
	text = re.sub(r'“', '.', str(text))
	text = re.sub(r'“', '.', str(text))
	text = re.sub(r'‟', '.', str(text))
	text = re.sub(r'”', '.', str(text))
	text = re.sub(r'\[', '.', str(text))
	text = re.sub(r'\]', '.', str(text))
	text = re.sub(r'\(', '.', str(text))
	text = re.sub(r'\)', '.', str(text))
	text = re.sub(r'\}', '.', str(text))
	text = re.sub(r'\{', '.', str(text))

	# turn commas into sentences
	#text = re.sub(r'\,', '.', str(text))

	# Replace ending punctuation
	#text = re.sub('\!', '.', str(text))
	#text = re.sub('\?', '.', str(text))
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

def save_words_recur(root_token, ancestor_position_list, ancestor_position, ancestor_word_pk):

	text = root_token.text
	pos_tag = root_token.tag_
	dependency_label = root_token.dep_
	sentence_position = root_token.i

	# clean up text for database
	text = word_cleaner.clean_word(text, pos_tag, dependency_label)

	# Save or update word
	word_pk = update_or_create_word(text, pos_tag, dependency_label, ancestor_word_pk)

	# Save ancestor position
	if not ancestor_position:
		ancestor_position = -1 # root word for the sentence
	ancestor_position_list[sentence_position] = ancestor_position

	# process child tokens recursively
	for child_token in root_token.children:
		save_words_recur(child_token, ancestor_position_list, sentence_position, word_pk)

def extract_template_features(sentence_doc, ancestor_position_list):
	pos_tags_list = []
	dependency_labels_list = []
	is_root_verb = False
	is_root_imperative = True
	

	for token in sentence_doc:

		pos_tags_list.append(token.tag_)
		dependency_labels_list.append(token.dep_)
		if token.dep_ == 'ROOT' and is_verb_position(token.tag_, token.dep_):
			is_root_verb = True
		if token.dep_ == 'expl' or 'sub' in token.dep_:
			is_root_imperative = False
	
	num_words = len(pos_tags_list)

	template = Template(is_root_verb=is_root_verb, is_root_imperative=is_root_imperative, num_words=num_words)
	template.set_pos_tags(pos_tags_list)
	template.set_dependency_labels(dependency_labels_list)
	template.set_ancestor_positions(ancestor_position_list)
	template.set_hash()

	if not Template.objects.filter(hash=template.hash): #already exists
		template.save()
	else:
		template = None

def nlp_with_rule_filtering(sentence):
# TODO: Re-write this. Is there a more efficient way to exclude words without having to reconstruct and then decontruct
#        the sentence again? I am doing so now because I need the children dependents returned by nlp() to match the
#        words going into the database, so I can't exclude words without re-processing.

	# Get initial tokens
	sentence_doc = nlp(sentence)
	
	# tools for template rules
	reconstructed_sentence = ''
	extra_properties = ['' for _ in sentence_doc] #preallocate slots
	replacement_text = list(extra_properties)

	
	for index, token in enumerate(sentence_doc):

		# --- --- Rules for template processing: (e.g. which kinds of words do we want to ignore?) --- ---

		# 1. Do not save punctuation into the db.
		#if ('punct' in token.dep_):
		#	extra_properties[index] = 'IGNORE'

		# 2. Do not save adverbs if they come directly after a verb. I find this really messes with correct tagging
		#     of some sentences from which auxiliary verbs have been removed.
		#     These could be inserted in line construction instead.
		#     Problematic example sentence:
		#		In the case of herbs, like goldenrod or daisy, the stem may be apparently all pith on the inside,
		# 		with only a thin outer coating of harder substance, not unlike bark, but usually green.
		if ('advmod' in token.dep_) and (index > 0 and 'VB' in sentence_doc[index-1].tag_ and not 'VBG' in sentence_doc[index-1].tag_):
			extra_properties[index] = 'IGNORE'

		# 3. If an auxiliary verb is a child of a verb that could be mistaken for yet another aux, replace the ambiguous verb with an explicit non-aux.
		for child in token.children:
			if ('MD' in child.tag_) or ('VB' in child.tag_ and 'aux' in child.dep_):
				if token.text.lower() in ['be', 'have', 'do']:
					replacement_text[index] = 'become'

		# 4. Do not save auxiliary verbs in the template db. These will be inserted in line construction instead.
		if ('MD' in token.tag_) or ('VB' in token.tag_ and 'aux' in token.dep_):
			extra_properties[index] = 'IGNORE'
		
		# --- --- Process rules --- ---
		if extra_properties[index] == 'IGNORE':
			continue
		
		if replacement_text[index]:
			newtext = replacement_text[index]
		else:
			newtext = sentence_doc[index].text

		# --- --- After all rules, reconstruct the sentence --- ---
		reconstructed_sentence = reconstructed_sentence + newtext + ' '
	
	# Get final tokens
	return nlp(reconstructed_sentence)

def save_words_and_template(sentence):
	
	
	# Ignore sentences with numerals
	if re.search(r'[0-9]+', sentence):
		return None

	# I'm gonna assume garbage if a sentence has more than one period.
	if sentence.count('.') > 1:
		return None

	# Tag the sentence
	sentence_doc = nlp_with_rule_filtering(sentence)

	# Save words and ancestor positions
	ancestor_position_list = [None for token in sentence_doc] # allocate storage slots
	root_token = get_root_token(sentence_doc)
	if not root_token:
		return None
	save_words_recur(root_token, ancestor_position_list, ancestor_position=None, ancestor_word_pk=None)

	# Extract template features and save if unique
	template = extract_template_features(sentence_doc, ancestor_position_list)

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