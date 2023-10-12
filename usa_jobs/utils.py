from typing import Tuple, List
import re
from wordhoard import Synonyms
from cachetools import cached


@cached(cache={})
def process_location(location: str, seperator=',') -> Tuple[str, str]:
    """
    split location into city & state
    assumption: last 2 are city & state
    (e.g. for input: Madera, Palo Alto, California, output is city=Palo Alto & state=California)
    also assumes city & state are harmonized from upstream e.g. state = California (CA not allowed)
    :param location: Comma seperated city & state
    :return: city & state
    """

    loc: List[str] = location.split(seperator)[-2:]  # assumption, last 2 are city & state
    city, state = loc[0].strip(), loc[1].strip()

    return city, state


@cached(cache={})
def process_keywords(keywords: str) -> List[str]:
    """
    Helper function to return processed keywords, by removing spaces & separating words
    e.g. input = ' system programming ' output = 'system' & 'programming'
    :param keywords: unprocessed keywords
    :return: processed keywords
    """
    return keywords.split()


@cached(cache={})
def get_synonymns(keyword: str) -> List[str]:
    """
    find synonyms of query keywords using wordhoard library.
    :param keyword: keyword
    :return: list of words synonymous to keyword
    """
    return Synonyms(keyword).find_synonyms()


@cached(cache={})
def get_keywords_to_search_for(raw_word: str) -> List[str]:
    """
    function return semantically matching words for queried words.
    :param raw_word: comma seperated string to format
    :param keywords: list of keywords to find corresponding semantically same words.
    :return: list of all semantically similar words
    """
    raw_words = raw_word.split(",")
    keywords = list(map(str.strip, raw_words))

    processed_keyword_set = set()
    print(f"Input keywords are: {keywords}")
    for keyword in keywords:
        processed_keyword_set.add(keyword)
        # find synonyms of query keywords using wordhoard library.
        synonym_list = get_synonymns(keyword)

        # these are the issues from wordhoard library, it doesn't raise exceptions for weirdness
        if 'No synonyms were found' in synonym_list or 'please verify that word' in synonym_list:
            continue

        print("Synonyms are: ")
        for synonym in synonym_list:
            print(synonym)
            if len(synonym) > 1:
                # this condition to dodge other issues that wordhoard might have.
                processed_keyword_set.update(set(process_keywords(synonym)))
        # synonyms = set(map(process_keywords, synonym_list))
        # processed_keyword_set.update(synonyms)

    return list(processed_keyword_set)
