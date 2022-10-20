from random import choices
from django.db import models

class BookFile(models.Model):
    filename = models.CharField(max_length=200)
    hash = models.CharField(max_length=32) # max length set for MD5 hash

class Word(models.Model):
    text = models.CharField(max_length=45)
    pos_tag = models.CharField(max_length=13)
    dependency_label = models.CharField(max_length=13, blank=True)
    ancestor = models.ForeignKey(to="Word", null=True, blank=True, on_delete=models.SET_NULL)
    count = models.IntegerField(default=1)

    def get_matching_word(self, text, pos_tag, dependency_label, ancestor=None):
	
        try:
            word = Word.objects.get(text=text, pos_tag=pos_tag, dependency_label=dependency_label, ancestor=ancestor)
        except Word.DoesNotExist:
            return None
        
        return word
    
    def update_or_create_word(self, text, pos_tag, dependency_label, ancestor_pk):

        if ancestor_pk:
            ancestor = Word.objects.get(pk=ancestor_pk)
        else:
            ancestor = None

        word = self.get_matching_word(text, pos_tag, dependency_label, ancestor)
        if word:
            word.count = word.count+1
            word.save()
        else:
            word = Word(text=text, pos_tag=pos_tag, dependency_label=dependency_label, ancestor=ancestor)
            word.save()
        
        return word.pk