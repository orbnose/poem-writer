import random

first_subj_dict = {
    'I': ['I','we'],
    'we': ['I','we'],
}
first_obj_dict = {
    'me': ['me','us'],
    'mine': ['mine','ours'],
    'myself': ['myself','ourselves'],
    'ours': ['mine','ours'],
    'ourself': ['myself','ourself'],
    'ourselves': ['myself','ourselves'],
    'us': ['me','us'],
}
first_poss_dict = {
    'mine': ['mine','ours'],
    'my': ['my','our'],
    'our': ['my','our'],
}
second_subj_dict = {
    'you': ['you','you'],
}
second_obj_dict = {
    'thee': ['thee','ye'],
    'thine': ['thine','thine'],
    'thou': ['thou','ye'],
    'thyself': ['thyself','yourselves'],
    'ye': ['thee','ye'],
    'you': ['you','you'],
    'yours': ['your','your'],
    'yourself': ['yourself','yourselves'],
    'yourselves': ['yourself','yourselves'],
}
second_poss_dict = {
    'thine': ['thine','thine'],
    'thy': ['thy','your'],
    'your': ['your','your'],
}
third_subj_dict = {
    'all': ['one','all'],
    'another': ['another','others'],
    'anybody': ['anybody','all'],
    'anyone': ['anyone','all'],
    'anything': ['anything','all things'],
    'both': ['either','both'],
    'each': ['each','all'],
    'either': ['either','both'],
    'enough': ['enough','enough things'],
    'everybody': ['everybody','all'],
    'everyone': ['everyone','all'],
    'everything': ['everything','all things'],
    'few': ['one', 'few'],
    'he': ['he','they'],
    'it': ['it','they'],
    'many': ['one','many'],
    'most': ['one','most'],
    'neither': ['neither','none'],
    'nobody': ['nobody','none'],
    'none': ['neither','none'],
    'nothing': ['nothing','none'],
    'one': ['one','many'],
    'other': ['other','others'],
    'others': ['other','others'],
    'several': ['one','several'],
    'she': ['she','they'],
    'some': ['one','some'],
    'somebody': ['somebody','all'],
    'someone': ['someone','all'],
    'something': ['something','all things'],
    'such': ['such','such things'],
    'that': ['that','these'],
    'these': ['this','these'],
    'they': ['she','they'],
    'this': ['this','these'],
    'those': ['that','those'],
    'what': ['what','what things'],
    'whatever': ['whatever','whatever things'],
    'which': ['which','which'],
    'whichever': ['whichever','whichever'],
    'whichsoever': ['whichsoever','whichsoever'],
    'who': ['who','who all'],
    'whoever': ['whoever','who all'],
    'whoso': ['whoso','who all'],
    'whosoever': ['whosoever','whosoever all'],
}
third_obj_dict = {
    'all': ['one','all'],
    'another': ['another','others'],
    'anybody': ['anybody','all'],
    'anyone': ['anyone','all'],
    'anything': ['anything','all things'],
    'both': ['either','both'],
    'each': ['each','all'],
    'either': ['either','both'],
    'enough': ['enough','enough things'],
    'everybody': ['everybody','all'],
    'everyone': ['everyone','all'],
    'everything': ['everything','all things'],
    'few': ['one', 'few'],
    'her': ['her','their'],
    'hers': ['hers','theirs'],
    'herself': ['herself','themselves'],
    'him': ['him','them'],
    'himself': ['himself','themselves'],
    'it': ['it','they'],
    'itself': ['itself','theirselves'],
    'many': ['one','many'],
    'most': ['one','most'],
    'neither': ['neither','none'],
    'nobody': ['nobody','none'],
    'none': ['neither','none'],
    'nothing': ['nothing','none'],
    'one': ['one','many'],
    'other': ['other','others'],
    'others': ['other','others'],
    'several': ['one','several'],
    'some': ['one','some'],
    'somebody': ['somebody','all'],
    'someone': ['someone','all'],
    'something': ['something','all things'],
    'such': ['such','such things'],
    'that': ['that','these'],
    'theirs': ['hers','theirs'],
    'theirself': ['herself','theirself'],
    'theirselves': ['herself','theirselves'],
    'them': ['her','them'],
    'themself': ['herself','themself'],
    'themselves': ['herself','themselves'],
    'these': ['this','these'],
    'this': ['this','these'],
    'those': ['that','those'],
    'what': ['what','what things'],
    'whatever': ['whatever','whatever things'],
    'which': ['which','which'],
    'whichever': ['whichever','whichever'],
    'whichsoever': ['whichsoever','whichsoever'],
    'whom': ['whom','whom'],
    'whomever': ['whomever','whomever'],
    'whomso': ['whomso','whomso'],
    'whomsoever': ['whomsoever','whomsoever'],
}
third_poss_dict = {
    'her': ['her','their'],
    'his': ['his','theirs'],
    'its': ['its','their'],
    'their': ['her','their'],
    'whose': ['whose','whose'],
    'whosever': ['whosever','whosever'],
    'whosesoever': ['whosesoever','whosesoever'],
}

def get_random_pronoun(position_dict, singular_lookup):
    position_list = list(position_dict.values())
    position_lookup = random.randrange(0, len(position_list))
    return position_list[position_lookup][singular_lookup]

def validate_voice(voice):
    if not (voice=='first' or voice=='second' or voice=='third'):
            raise ValueError('invalid voice input')

def validate_singular(singular):
    if not (type(singular)==bool):
        raise ValueError('invalid singular input')

class Pronoun():
    def __init__(self):

        self.dictionary = {
            'first': {
                'subj': first_subj_dict,
                'obj': first_obj_dict,
                'poss': first_poss_dict,
            },
            'second': {
                'subj': second_subj_dict,
                'obj': second_obj_dict,
                'poss': second_poss_dict,
            },
            'third': {
                'subj': third_subj_dict,
                'obj': third_obj_dict,
                'poss': third_poss_dict,
            }
        }
    
    def transform(self,pronoun_text, voice, dependency_label, singular, force_selection):
        
        # validate voice
        validate_voice(voice)
        # validate dependency_label
        if not (dependency_label=='subj' or dependency_label=='obj' or dependency_label=='poss'):
            raise ValueError('invalid dependency label input')
        # validate singular
        validate_singular(singular)
        # validate force_selection
        if not (type(force_selection)==bool):
            raise ValueError('invalid force selection input')

        # setup dictionary controls
        if singular:
            lookup = 0
        else:
            lookup = 1
        
        # handle lookup
        #  self.dictionary[voice][dependency_position]['pronoun'] = [ 'singular', 'plural' ]
        try:
            position_dict = self.dictionary[voice][dependency_label]
            number_dict = position_dict[pronoun_text]
            if number_dict:
                return number_dict[lookup]

        # pronoun not found in target list - choose one at random or just return the input.
        except KeyError:
            if force_selection:
                #TODO: make swappable random selection model
                return get_random_pronoun(position_dict, lookup)
            return pronoun_text