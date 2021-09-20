import requests
import json

URL = 'http://34.67.195.184/bck'  # constant url
API = requests.get(URL, stream=True)  # request for the json

WORDS_DICTIONARY = {}
HASHTAGS_DICTIONARY = {}
TIME_DICTIONARY = {}

def import_tweet(request):
    '''
    importing a single tweet
    :param request: api request
    :return: a DICTIONARY which represents the tweet
    '''
    tweet = request.raw.read(50).decode("utf-8")  # reading first 50 bytes which are definitely not a full tweet

    full_tweet = False
    while not full_tweet:  # loop until we have the whole tweet
        tweet += request.raw.read(1).decode("utf-8")  # single byte
        if tweet[-1] == "}":  # end of a dictionary --> "}"
            try:
                # if the column was an end of a tweet,
                # the transformation to json dictionary should succeed
                request = json.loads(tweet)
                full_tweet = True
            except:
                # otherwise, it means the end of an internal dictionary inside the tweet
                pass

    json_tweet = json.loads(tweet)
    return json_tweet

def update_words(new_words, dictionary):
    '''
    updates the words dictionary
    :param new_words: list of new words
    :param dictionary: the exists dictionary
    :return: the updated words dictionary
    '''
    for word in new_words:
        if word.lower() in dictionary:  # word already there
            val = dictionary[word.lower()]  # current value of the word
            dictionary.update({word.lower():val + 1})  # raising the value by 1
        else:  # first time the word shows
            dictionary.update({word.lower():1})  # gets the value 1

    # sorting the dictionary by values from the highest values to the lowest
    doct_by_value = {k: v for k, v in sorted(dictionary.items(), key= lambda v: v[1], reverse=True)}
    return doct_by_value

def update_hashtags(list_of_dicts, dictionary):
    '''
    updates the words dictionary
    :param list_of_dicts: each hashtag is a dictionary inside the list -- > [{'text': 'TEXT', 'indices': [int, int]}]
    :param dictionary: the exists dictionary
    :return: the updated hashtags dictionary
    '''
    hashtags = []  # only the words of the hashtags
    if len(list_of_dicts) == 0:  # nothing to update
        return dictionary

    # the code is here if there is at least one hashtag in the tweet
    for dict in list_of_dicts:  # every dictionary as it's template mentioned in the beginning of the method
        hashtags.append(dict['text'])  # the word itself

    # same way as in update_words()
    for word in hashtags:
        if word.lower() in dictionary:
            val = dictionary[word.lower()]
            dictionary.update({word.lower():val + 1})
        else:
            dictionary.update({word.lower():1})

    doct_by_value = {k: v for k, v in sorted(dictionary.items(), key= lambda v: v[1], reverse=True)}
    return doct_by_value

def update_average(new_time, dictionary):
    '''
    updates the new time in the dictionary
    :param new_time: the upload time of the new tweet
    :param dictionary: the exists dictionary
    :return: integer of the new tweets per second average
    '''
    if new_time in dictionary:
        value = dictionary[new_time]
        dictionary.update({new_time:value + 1})
    else:
        dictionary.update({new_time:1})

    return dictionary

def calculate_average(dictionary):
    '''
    calculates the average
    :param dictionary: the time dictionary
    :return: integer represents the average tweets per second
    '''

    # the time is updated, but we should notice
    # that the first and/or the last item in the dictionary
    # might be also only half a second (not a full one),
    # so well pop them items out
    keys = list(dictionary)
    if len(keys) > 2:

        dictionary.pop(keys[0])
        dictionary.pop(keys[-1])

    # quick math
    amount_of_keys = len(list(dictionary))
    sum_of_tweets = 0
    for time in dictionary:
        sum_of_tweets += dictionary[time]
    avg_tweets = sum_of_tweets/amount_of_keys

    return avg_tweets

def update_data(tweet_dict):
    '''
    updates the data structures with a new tweet, recalculating the stats asked
    :return: words dictionary, hashtags dictionary, average integer
    '''
    global WORDS_DICTIONARY
    global HASHTAGS_DICTIONARY
    global TIME_DICTIONARY

    # words
    tweet_text = tweet_dict['text']  # String (template --> "RT @name text...")
    tweet_text_list = tweet_text.split(' ')[2:]  # after the "RT" and the @name --> only words
    WORDS_DICTIONARY = update_words(tweet_text_list, WORDS_DICTIONARY)  #

    # hashtags
    tweet_hashtags = tweet_dict['entities']['hashtags']
    HASHTAGS_DICTIONARY = update_hashtags(tweet_hashtags, HASHTAGS_DICTIONARY)

    # adding the time to the time dictionary
    upload_time = tweet_dict['created_at'].split(' ')[3]
    TIME_DICTIONARY = update_average(upload_time, TIME_DICTIONARY)

    return WORDS_DICTIONARY, HASHTAGS_DICTIONARY, TIME_DICTIONARY

def print_data():
    global AVERAGE

    print('TOP 10 WORDS:\n')
    i = 0
    for item in WORDS_DICTIONARY:
        print(str(i + 1) + ".", item, "-->", WORDS_DICTIONARY[item])
        i += 1
        if i == 10:
            break

    print('\nTOP 10 HASHTAGS:\n')
    i = 0
    for item in HASHTAGS_DICTIONARY:
        print(str(i + 1) + ".", item, "-->", HASHTAGS_DICTIONARY[item])
        i += 1
        if i == 10:
            break

    print('\nAVERAGE TWEETS PER SECOND:', AVERAGE)


def analize(amount_of_tweets):
    for num in range(0, amount_of_tweets):
        if amount_of_tweets > 100:
            if num == amount_of_tweets/2:
                print('Half way there...')
        tweet = import_tweet(API)
        update_data(tweet)

analize(500)
AVERAGE = calculate_average(TIME_DICTIONARY)
print_data()






