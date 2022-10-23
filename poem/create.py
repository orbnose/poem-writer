from .chooser import TemplateChooser, WordChooser

wordChooser = WordChooser()
templateChooser = TemplateChooser()

class Line():
    #num_words is int for template selection
    #singular is boolean for subject-verb agreement
    #voice is a value of ["first", "second", "third"] for subject-verb agreement
    #verb_tense is a value accepted by mlconjug3 for conjugation (see VerbTransformer).
    
    def _init__(self, num_words: int, singular: str, voice: str, verb_tense: str, dependency_labels: list, pos_tags: list, ancestor_positions: list):
        self.num_words = num_words
        self.singular = singular
        self.voice = voice
        self.verb_tense = verb_tense
        self.dependency_labels = dependency_labels
        self.pos_tags = pos_tags
        self.ancestor_positions = ancestor_positions

        #pre-allocate word slots
        self.word_texts = [None for _ in self.dependency_labels]

    def choose_words(self):
         for position, _ in enumerate(self.dependency_labels):

            # set up data   
            pos_tag = self.pos_tags[position]
            dependency_label = self.dependency_labels[position]
            ancestor_position = self.ancestor_positions[position]
            ancestor_pos_tag = self.pos_tags[ancestor_position]
            require_voice_agreement = False

            # Correct potential inter-word selection problems with the following rules:

            # 1. Make sure voice matches between verbs (but not gerunds/infinites) and nouns. 
            #     1st or 2nd voice means nouns must be replaced with pronouns.
            if ('VB' in ancestor_pos_tag and 'VBG'!= ancestor_pos_tag and 'VB' != ancestor_pos_tag and 'NN' in pos_tag and (self.voice == 'first' or self.voice=='second') ):
                pos_tag = 'PRP'
                self.pos_tags[position] = pos_tag
                require_voice_agreement = True

            # 2. A possessive pronoun cannot be in front of a pronoun.
            #     If this happens, replace the possessive with an adjective.
            if ( ('PRP'==ancestor_pos_tag or 'WP'==ancestor_pos_tag) and ('PRP$'==pos_tag or 'WP$'==pos_tag) ):
                pos_tag = 'JJ'
                dependency_label = 'amod'
                self.pos_tags[position] = pos_tag
                self.dependency_labels[position] = dependency_label
            
            # Choose words


    def get_line_text(self) -> str:
        ret_string = ''
        for text in self.word_texts:
            if text == '.':
                ret_string = ret_string[:-1] #get rid of space before punctuation
            ret_string = ret_string + text + ' '

def makeline(num_words, singular, voice, verb_tense):
    
    # get template info
    template = templateChooser.choose(num_words=num_words)

    # package data and choose words
    line = Line(
        num_words = num_words,
        singular = singular,
        voice = voice,
        verb_tense = verb_tense,
        dependency_labels = template.get_dependency_labels(),
        pos_tags = template.get_pos_tags(),
        ancestor_positions = template.get_ancestor_positions()
    )
    line.choose_words()

   