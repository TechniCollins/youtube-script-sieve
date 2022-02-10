from django.shortcuts import render
import csv # to read demonetized words file
from django.conf import settings

from textblob import Word # for synonyms

import datetime

import json

from django.http import HttpResponse


def index(request):
    context = {}
    return render(request, 'index.html', context)


'''
Textblob, and other NLP tools remove hashtags and
other characters that are used in social media all the
time. So they're not a nice solution for this specific
application. We'll make our own simple tokenizer instead.
To maintain the formatting, I replaced (?,.) with three
leading zeros and two trailing zeros instead of nothing.
This way, we can reform our original paragraph(s)
by replacing "   .  " with "."
'''
def tokenize(text):
    # characters = [".", ",", "?"]

    cleaned_text = text

    # for character in characters:
    #     if character in text:
    #         cleaned_text = cleaned_text.replace(character, "")

    # we'll use this only if/when we have more characters to remove
    # for now, chaining .replace() is the fastest

    cleaned_text = cleaned_text.replace(".", "   .  ").replace(",", "   ,  ").replace("?", "   ?  ")


    # convert to lowercase and split into
    # list of words
    cleaned_text = cleaned_text.split(" ")
    # removed .lower() to maintain most of the formatting
    # when displaying results

    return cleaned_text


def getSynonyms(word):
    synonym_list = []

    # try to get synonyms
    try:
        synonyms = Word(word)
        for synset in synonyms.synsets:
            for lemma in synset.lemmas():
                synonym = lemma.name()
                if synonym.lower() != word.lower():
                    synonym_list.append(synonym)
        # Get user defined synonyms
        with open(f"{settings.BASE_DIR}/words/synonyms.json", "r") as f:
            user_synonyms = json.load(f).get(word, [])
            # if list is not empty, append values to
            # synonyms list
            for i in user_synonyms:
                synonym_list.insert(0, i)
    except Exception as e:
        print(e)
        synonym_list = ["No associated words"]

    if not synonym_list:
        synonym_list = ["No associated words"]

    return synonym_list


def checkDemonetizationWords(text):
    start_time = datetime.datetime.now()

    with open(f"{settings.BASE_DIR}/words/all_words.csv", "r") as dwords_file:
        dwords = csv.reader(dwords_file, delimiter=',')

        # We are forming a dictionary of demonetized word objects, with the word
        # as key and {color, severity} as value.
        dword_objects = {}

        # Results will be cached in future to avoid creating these objects all the time.
        # Redo only when file has changed
        for index, dword in enumerate(dwords):
            dword_objects[dword[0].lower()] = {"color": dword[1], "severity": dword[2]}


    # Form a list of all words in text
    # Our assumption at the moment is the text
    # will be < 3500 words, so this won't have
    # severe perfomance issues

    script_words = tokenize(text)

    # This list will help us reform the original text with
    # the bad words highlited
    highlited_text_list = []

    for index, word in enumerate(script_words):
        # make lowercase before comparing
        get_matching_bad_word = dword_objects.get(word.lower())

        if get_matching_bad_word:
            color = get_matching_bad_word.get("color")
            severity = get_matching_bad_word.get("severity")

            if color == 'yellow':
                synonym_list = getSynonyms(word)
                highlited_text_list.append(
                    f"<mark data-toggle = 'tooltip' title = '{','.join(synonym_list)}' data-placement = 'top' class = 'red' onclick='showSynonymForm(this);'>{word}</mark>"
                )
            else:
                if int(severity) > 0 and int(severity) <= 3:
                    synonym_list = getSynonyms(word)
                    highlited_text_list.append(
                        f"<mark data-toggle = 'tooltip' title = '{','.join(synonym_list)}' data-placement = 'top' class = 'yellow' onclick='showSynonymForm(this);'>{word}</mark>"
                    )
                elif int(severity) >= 4:
                    synonym_list = getSynonyms(word)
                    highlited_text_list.append(
                        f"<mark data-toggle = 'tooltip' title = '{','.join(synonym_list)}' data-placement = 'top' class = 'orange' onclick='showSynonymForm(this);'>{word}</mark>"
                    )
                else:
                    highlited_text_list.append(word)
        else:
            highlited_text_list.append(word)

    highlited_text = (" ".join(highlited_text_list)).replace("   .  ", ".").replace("   ,  ", ",").replace("   ?  ", "?")

    print(f"Done in {datetime.datetime.now() - start_time} seconds")

    return highlited_text


def analyzeText(request):
    text = request.POST.get("text")
    bad_words = checkDemonetizationWords(text)
    context = {"text": bad_words}
    return render(request, 'rendered_results.html', context)


def addSynonym(request):
    word = request.GET.get("word")
    synonym = request.GET.get("synonym")
    # Save new values to file
    with open(f"{settings.BASE_DIR}/words/synonyms.json", "r") as fr:
        user_synonyms = json.load(fr)
        # Check if word already exists
        # append new value if it does,
        # otherwise add new
        if user_synonyms.get(word):
            user_synonyms[word].insert(0, synonym)
        else:
            user_synonyms[word] = [synonym]

    with open(f"{settings.BASE_DIR}/words/synonyms.json", "w") as fw:
        fw.write(json.dumps(user_synonyms))

    return HttpResponse("Synonym added")
