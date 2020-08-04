"""
Flags in unicode are made of two regional indicator symbols that are
not normal letters but are basically A to Z.

This Python script finds the longest word that can be spelt using
unicode flags, the longest word that does not contain a flag, and
also words that are semordnilap/palindrome when spelt using flags.

- AceLewis
"""

import re

import requests
from bs4 import BeautifulSoup


def shift_string(string, shift):
    """Shift all characters in a string by this amount"""
    return ''.join(chr(ord(x)+shift) for x in string)


def text_to_flag(text):
    """Lowercase a-z to regional indicator symbols"""
    return shift_string(text, flag_offset)


def flag_to_text(flag_string):
    """Regional indicator symbols to lowercase a-z"""
    return shift_string(flag_string, -flag_offset)


def get_hex(string):
    """Get the hex codes for a string seperated by a hyphen"""
    return '-'.join(hex(ord(x))[2:] for x in string)


def get_twemoji_codepoint_name_dict(file_name):
    """
    Works for both twemoji amazing and awesome.
    Returns a dictionary with all the codepoints as the key and the name as the value.
    Input the filepath to the css used for the website/
    """
    regex = (r"\.twa-([a-z0-9\-]*)\s*{\s*background-image:\s*url"
             r"\(\"https:\/\/twemoji\.maxcdn\.com\/[a-z0-9\/]*\/svg\/([a-z0-9\-]*)\.svg\"\);?\s*}")
    with open(file_name, 'r') as file:
        data = file.read()
    return dict(reversed(x)for x in re.findall(regex, data))


def get_emoji_name(emoji, emoji_names):
    """Gets the name of an emoji"""
    return emoji_names[get_hex(emoji)]


def text_to_twemoji_flag(word, emoji_names):
    """Input a string that can be spelt with flags and it will output the twemoji flags"""
    it_text = iter(text_to_flag(word))
    return ''.join(f'<i class="twa twa-{get_emoji_name(x+y, emoji_names)}"></i>'
                   for x, y in zip(it_text, it_text))


def text_to_twemoji_ris(word, emoji_names):
    """Input a string ([a-z]*) and it will output the twemoji RIS"""
    return ''.join(f'<i class="twa twa-{get_emoji_name(x, emoji_names)}"></i>'
                   for x in text_to_flag(word))


def see_if_word_can_be_spelt(word, country_codes):
    """
    See if a word can be spelt from the concatination of
    country codes of flags availible in emoji
    """
    # To be spelt by flags it has to be even an length long
    if len(word) % 2 == 1:
        return False
    elif len(word) == 0:
        return True
    elif text_to_flag(word[:2]) in country_codes:
        return see_if_word_can_be_spelt(word[2:], country_codes)
    else:
        return False


def contains_no_flag(word, regex_for_flag):
    """Checks a string to see that it contains no characters that could make a flag"""
    return not re.findall(regex_for_flag, text_to_flag(word))


def filter_all_input_words(word_list, function, function_input):
    """Filters a word list by the function provided"""
    words = []
    with open(word_list) as file:
        for line in file:
            if function(line.strip().lower(), function_input):
                words.append(line.strip())
    return words


def get_all_words_that_can_be_spelt(word_list, all_flags):
    """Returns all words that can be spelt using the two characters in unicode flags"""
    return filter_all_input_words(word_list, see_if_word_can_be_spelt, all_flags.keys())


def get_all_words_with_no_flags(word_list, regex_for_flag):
    """Returns all words that contain no flags"""
    return filter_all_input_words(word_list, contains_no_flag, regex_for_flag)


def generic_all_semordnilap_words(reverse_function, word_that_can_be_spelt):
    """Get all semordnilap and palindrome words"""
    semordnilap_words = []
    for word in word_that_can_be_spelt:
        if len(word) > 2 and reverse_function(word) in word_that_can_be_spelt:
            semordnilap_words.append(tuple(sorted([word, reverse_function(word)])))
    # Semordnilap words are counted twice, so filter them
    return list(set(semordnilap_words))


def reverse_word_by_flag(word):
    """Reverse a word in pairs of two"""
    it_text = iter(reversed(word))
    return ''.join((y+x for x, y in zip(it_text, it_text)))


def get_all_flag_semordnilap_words(word_that_can_be_spelt):
    """Get all semordnilap and palindrome words"""
    return generic_all_semordnilap_words(reverse_word_by_flag, word_that_can_be_spelt)


def get_all_true_semordnilap_words(word_that_can_be_spelt):
    """Get all semordnilap and palindrome words"""
    return generic_all_semordnilap_words(lambda x: x[::-1], word_that_can_be_spelt)


def print_breakdown(word, all_flags):
    """Prints the breakdown of a word into the two characters in unicode flags"""
    print("Breakdown:")
    it_text = iter(word)
    for x, y in zip(it_text, it_text):
        print(f'{text_to_flag(x+y)}: {all_flags[text_to_flag(x+y)]}')
    print('')


def print_breakdown_markdown(word, all_flags, twemoji_awesome_names):
    """Prints the breakdown of a word into each flag for use on my blog"""
    print("| Flag |&nbsp;Code&nbsp;| Country name |")
    print("|------|----------------|--------------|")
    it_text = iter(word)
    for x, y in zip(it_text, it_text):
        flag = text_to_twemoji_flag(x+y, twemoji_awesome_names)
        print(f'|&nbsp;{flag}|&nbsp;&nbsp; {(x+y).upper()}|{all_flags[text_to_flag(x+y)]}|')
    print('')


def file_length(file_name):
    """Get the number of lines in a file"""
    with open(file_name) as file:
        for line_number, _ in enumerate(file, 1):
            pass
    return line_number


def get_flags_emojipedia():
    """Scraping the data for emoji flags from emojipedia"""
    url = 'https://emojipedia.org/flags/'
    request = requests.get(url)
    soup = BeautifulSoup(request.text, 'html.parser')
    flag_content = soup.find('div', attrs={'class': 'content'})
    flag_list = flag_content.find('ul', attrs={'class': 'emoji-list'})
    # The rows that are flags for countries are two characters long
    all_flags = filter(lambda x: len(x.span.text) == 2, flag_list.find_all('li'))
    return dict(x.text.split(' Flag: ') for x in all_flags)


def get_flags_wikipedia():
    """
    Scraping the data for flags from Wikipedia because emojipedia shows a captcha
    when you connect using a VPN.
    """
    url = 'https://en.wikipedia.org/wiki/Regional_Indicator_Symbol'
    request = requests.get(url)
    soup = BeautifulSoup(request.text, 'html.parser')
    flag_rows = soup.find('table').find('tbody').find_all('tr')[1:]
    return dict(x.text.split('\n')[1:4:2] for x in flag_rows)


if __name__ == "__main__":
    # This is not in a main function because twemoji_names and other variables will still be in
    # the variable explorer. I am just writing this for my blog.
    # The offset from lowercase a-z to the regional indicator symbols 🇦-🇿
    flag_offset = 127365
    # I got the word list from https://github.com/dwyl/english-words
    word_list = 'words_alpha.txt'
    # Scraping the data for flags from wikipedia because captchas on emojiipedia
    all_flags = get_flags_wikipedia()
    # Compile regex here so it is not compiled on every function call
    regex_for_flag = re.compile("("+"|".join(all_flags.keys())+")")
    # Not used in this but I want it in the variable explorer so I can use text_to_twemoji_flag etc
    twemoji_names = get_twemoji_codepoint_name_dict('twemoji-amazing.css')
    # Work out the words that have the properties we are looking for
    word_that_can_be_spelt = get_all_words_that_can_be_spelt(word_list, all_flags)
    word_with_no_flags = get_all_words_with_no_flags(word_list, regex_for_flag)
    true_semordnilap_words = get_all_true_semordnilap_words(word_that_can_be_spelt)
    flag_semordnilap_words = get_all_flag_semordnilap_words(word_that_can_be_spelt)
    # Calculate the percentage of words for each group
    total_number_of_words = file_length(word_list)
    percentage_can_be_spelt = len(word_that_can_be_spelt)/total_number_of_words
    percentage_no_flag = len(word_with_no_flags)/total_number_of_words
    percentage_true_semordnilap = len(true_semordnilap_words)/total_number_of_words
    percentage_flag_semordnilap = len(flag_semordnilap_words)/total_number_of_words
    # Print all the data:
    # Words that can be spelt with flags
    print(f"Number of words that can be spelt by flags {len(word_that_can_be_spelt)} "
          f"({percentage_can_be_spelt:.2%})")
    max_len = len(max(word_that_can_be_spelt, key=len))
    longest_words = list(filter(lambda x: len(x) >= max_len, word_that_can_be_spelt))
    # Other notable words that I like.
    print(f"Longest word(s) of length {max_len}")
    for word in longest_words:
        print(f"{word} : {text_to_flag(word)}")
        print_breakdown(word, all_flags)
    # Words that contain no flags
    print(f"Number of words that can be spelt without flags {len(word_with_no_flags)} "
          f"({percentage_no_flag:.2%})")
    max_len = len(max(word_with_no_flags, key=len))
    longest_words_no_flag = [*filter(lambda x: len(x) == max_len, word_with_no_flags)]
    print(f"Longest word(s) of length {max_len}")
    for word in longest_words_no_flag:
        print(f"{word} : {text_to_flag(word)}")
    # Words that are true semordnilaps/palindromes
    max_len = len(max(true_semordnilap_words, key=lambda x: len(x[0]))[0])
    longest_words = [*filter(lambda x: len(x[0]) == max_len, true_semordnilap_words)]
    print(f"\nLongest true semordnilap and palindrome word(s) of length {max_len}")
    for word1, word2 in longest_words:
        print(f"{word1}, {word2} : {text_to_flag(word1)}, {text_to_flag(word2)}")
        # print_breakdown(word1, all_flags)
    # Words that are flag palindromes/semordnilaps
    max_len = len(max(flag_semordnilap_words, key=lambda x: len(x[0]))[0])
    longest_words = [*filter(lambda x: len(x[0]) == max_len, flag_semordnilap_words)]
    print(f"\nLongest flag semordnilap and palindrome word(s) of length {max_len}")
    for word1, word2 in longest_words:
        print(f"{word1}, {word2} : {text_to_flag(word1)}, {text_to_flag(word2)}")
        # print_breakdown(word1, all_flags)
