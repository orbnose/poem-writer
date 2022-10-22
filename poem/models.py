import json
import hashlib
from django.db import models

class BookFile(models.Model):
    filename = models.CharField(max_length=200)
    hash = models.CharField(max_length=32) # max length set for MD5 hash

class Word(models.Model):
    text = models.CharField(max_length=45)
    pos_tag = models.CharField(max_length=13)
    dependency_label = models.CharField(max_length=13, blank=True)
    ancestor = models.ForeignKey(to="Word", null=True, blank=True, on_delete=models.SET_NULL)
    count = models.PositiveBigIntegerField(default=1)

def get_matching_word(text, pos_tag, dependency_label, ancestor=None):

    try:
        word = Word.objects.get(text=text, pos_tag=pos_tag, dependency_label=dependency_label, ancestor=ancestor)
    except Word.DoesNotExist:
        return None
    
    return word

def update_or_create_word(text, pos_tag, dependency_label, ancestor_pk):

        if ancestor_pk:
            ancestor = Word.objects.get(pk=ancestor_pk)
        else:
            ancestor = None

        word = get_matching_word(text, pos_tag, dependency_label, ancestor)
        if word:
            word.count = word.count+1
            word.save()
        else:
            word = Word(text=text, pos_tag=pos_tag, dependency_label=dependency_label, ancestor=ancestor)
            word.save()
        
        return word.pk

def set_json(input_list):
    return json.dumps(input_list)

class Template(models.Model):
    
    # JSONFields might be better in the long run for these 3, but not using it since I'm not sure what my backend will be.
    pos_tags_json = models.CharField(max_length = 500) # assuming tagging by spacy
    dependency_labels_json = models.CharField(max_length = 500) # assuming tagging by spacy
    dependency_order_json = models.CharField(max_length=500) # order of dependency labels list indices sorted by least dependent (root) to most

    hash = models.CharField(max_length=32) # max length set for MD5 hash
    num_words = models.PositiveIntegerField()
    is_root_verb = models.BooleanField(default=True)
    is_root_imperative = models.BooleanField(default=True)

    def set_pos_tags(self, pos_tags_tuple):
        self.pos_tags_json = set_json(pos_tags_tuple)
    
    def set_dependency_labels(self, dependency_labels_tuple):
            self.dependency_labels_json = set_json(dependency_labels_tuple)
    
    def set_dependency_order(self, dependency_order_tuple):
        self.dependency_order_json = set_json(dependency_order_tuple)

    def get_pos_tags(self):
        return json.loads(self.pos_tags_json)
    
    def get_dependency_labels(self):
        return json.loads(self.dependency_labels_json)
    
    def get_dependency_order(self):
        return json.loads(self.dependency_order_json)
    
    def set_hash(self):
        if not (self.pos_tags_json and self.dependency_labels_json):
            raise ValueError('missing required info for template hash')
        hash_string = self.pos_tags_json + self.dependency_labels_json
        self.hash = hashlib.md5(hash_string.encode()).hexdigest()
        return self.hash
        