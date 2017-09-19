#!/usr/bin/python
# -*- coding: UTF-8 -*- 
import re, os

def ReadInAttributes(keywords_file):
    "This function is used to read in attribute name"
    attribute_list = list()
    input_data = open(keywords_file, "r")
    for eachLine in input_data:
        if eachLine != "" and eachLine != "\n":
            input_str = eachLine.replace("\n", "")
            input_str = input_str.replace("\ufeff", "")
            fields = input_str.split("\t")
            field_name = fields[0]
            attr_name = field_name.split("_")[0]
            if attr_name not in attribute_list and attr_name != "":
                attribute_list.append(attr_name)
    input_data.close()
    return attribute_list


def ReadInKeyWords(keywords_file):
    "This function is used to read in keywords"
    keywords_dict = dict()
    input_data = open(keywords_file, "r")
    for eachLine in input_data:
        if eachLine != "" and eachLine != "\n":
            input_str = eachLine.replace("\n", "")
            input_str = input_str.replace("\ufeff", "")
            fields = input_str.split("\t")
            field_name = fields[0]
            attr_name = field_name.split("_")[0]
            if attr_name not in keywords_dict.keys():
                keywords_dict[attr_name] = dict()
            word_type = field_name[len(attr_name)+1:]
            if word_type not in keywords_dict[attr_name].keys():
                keywords_dict[attr_name][word_type] = list()
            if len(fields) > 1:
                for eachWord in fields[1:]:
                    if eachWord != "" and eachWord not in keywords_dict[attr_name][word_type]:
                        keywords_dict[attr_name][word_type].append(eachWord)
    input_data.close()
    for eachAttr in keywords_dict.keys():
        for eachType in keywords_dict[eachAttr].keys():
            keywords_dict[eachAttr][eachType].sort(key = len, reverse = True)
    return keywords_dict


def ReadInReviews(review_file):
    "This function is used to read reviews"
    sentences = list()
    punctuation = {" ", "，", "。", "！", "~", "@", "#", "￥", "%", "……", "&", "*", "（", "）", "？", "：", "；", ".", "...", "，", "。", "!", "～", "(", ")", "虽然", "但是", "不过", "但", "只是", "于是", "然后", "然而", "所以", "因为", "由于", "不管","啊","吗","呢","吧"}
    review_data = open(review_file, "r")
    for eachLine in review_data:
        if eachLine != "\n" and eachLine != "":
            small_sent = list()
            input_str = eachLine.replace("\n", "")
            input_str = input_str.replace("\ufeff", "")
            input_str = input_str.replace("\ue00e", "")
            input_str = input_str.replace('"', "")
            input_str = input_str.replace("'", "")
            if input_str != "":
                fields = input_str.split("\t")
                review = fields[0]
                cleaned_review = "".join(review)
                for eachPunc in punctuation:
                        if eachPunc in review:
                            cleaned_review = cleaned_review.replace(eachPunc, ",")
                split_review = cleaned_review.split(",")
                for eachOne in split_review:
                    if eachOne != '':
                        small_sent.append(eachOne)
            sentences.append([review, small_sent])
    review_data.close()
    return sentences
    

def RemoveStopWords(stopwords_file):
    "This function is used to remove stop words from the review"
    stopwords_list = list()
    input_file = open(stopwords_file, "r")
    for eachLine in input_file:
        if eachLine != "\n" and eachLine != "":
            words_str = eachLine.replace("\n", "")
            words_str = words_str.replace("\ufeff", "")
            words = words_str.split(",")
            for each in words:
                stopwords_list.append(each)
    input_file.close()
    stopwords_list.sort(key = len, reverse = True)
    return stopwords_list


def AnalyzeEachSentence(keywords_dict, keywords_list, eachSentence, stopwords_file):
    "This function is used to analyze each sentence"
    sentence_result = list()
    eachSen = "".join(eachSentence)
    print(eachSen)
    words_list, words_type, words_index = list(), list(), list()
    noun_counter, adj_counter, adv_counter, verb_counter, conj_counter = 0, 0, 0, 0, 0
    new_sentence = "".join(eachSentence)
    "Remove stop words"
    stopwords_list = RemoveStopWords(stopwords_file)
    for eachWord in stopwords_list:
        if eachWord in eachSen:
            eachSen = eachSen.replace(eachWord, "*"*len(eachWord))
    buffer_sentence = "".join(eachSen)
    buffer_new_sentence = "".join(eachSen)
    
    for eachKeyWord in keywords_list:
        if eachKeyWord in buffer_sentence:
            new_word = re.compile(eachKeyWord).findall(buffer_sentence)
            for eachAttr in keywords_dict.keys():
                for eachType in keywords_dict[eachAttr]:
                    if eachKeyWord in keywords_dict[eachAttr][eachType] and (eachType == "Neu_Noun" or eachType == "Pos_Noun" or eachType == "Neg_Noun"):
                        for each in re.compile(eachKeyWord).findall(buffer_sentence):
                            eachIndex = buffer_sentence.index(each)
                            new_sentence = new_sentence[:buffer_new_sentence.index(each)] + "<" + eachKeyWord + ">" + new_sentence[buffer_new_sentence.index(each)+len(each):]
                            buffer_new_sentence = buffer_new_sentence[:buffer_new_sentence.index(each)] + "*"*(len(eachKeyWord)+2) + buffer_new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                            buffer_sentence = buffer_sentence[:eachIndex] + "*"*len(each) + buffer_sentence[eachIndex+len(each):]
                            words_list.append(each)
                            words_index.append(eachIndex)
                            if eachType == "Neu_Noun":
                                words_type.append("Neu_Noun")
                            elif eachType == "Pos_Noun":
                                words_type.append("Pos_Noun")
                            elif eachType == "Neg_Noun":
                                words_type.append("Neg_Noun")
                            else:
                                pass
                        noun_counter = noun_counter + len(new_word)
                    elif eachKeyWord in keywords_dict[eachAttr][eachType] and (eachType == "Pos_Verb" or eachType == "Neg_Verb"):
                        for each in re.compile(eachKeyWord).findall(buffer_sentence):
                            eachIndex = buffer_sentence.index(each)
                            new_sentence = new_sentence[:buffer_new_sentence.index(each)] + "(" + eachKeyWord + ")" + new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                            buffer_new_sentence = buffer_new_sentence[:buffer_new_sentence.index(each)] + "*"*(len(eachKeyWord)+2) + buffer_new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                            buffer_sentence = buffer_sentence[:eachIndex] + "*"*len(eachKeyWord) + buffer_sentence[eachIndex+len(eachKeyWord):]
                            words_list.append(each)
                            words_index.append(eachIndex)
                            if eachType == "Pos_Verb":
                                words_type.append("Pos_Verb")
                            elif eachType == "Neg_Verb":
                                words_type.append("Neg_Verb")
                            else:
                                pass
                        verb_counter = verb_counter + len(new_word)
                    elif eachKeyWord in keywords_dict[eachAttr][eachType] and (eachType == "Neu_Adj" or eachType == "Pos_Adj" or eachType == "Neg_Adj"):
                        for each in re.compile(eachKeyWord).findall(buffer_sentence):
                            eachIndex = buffer_sentence.index(each)
                            new_sentence = new_sentence[:buffer_new_sentence.index(each)] + "[" + eachKeyWord + "]" + new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                            buffer_new_sentence = buffer_new_sentence[:buffer_new_sentence.index(each)] + "*"*(len(eachKeyWord)+2) + buffer_new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                            buffer_sentence = buffer_sentence[:eachIndex] + "*"*len(eachKeyWord) + buffer_sentence[eachIndex+len(eachKeyWord):]
                            words_list.append(each)
                            words_index.append(eachIndex)
                            if eachType == "Neu_Adj":
                                words_type.append("Neu_Adj")
                            elif eachType == "Pos_Adj":
                                words_type.append("Pos_Adj")
                            elif eachType == "Neg_Adj":
                                words_type.append("Neg_Adj")
                            else:
                                pass
                        adj_counter = adj_counter + len(new_word)
                    elif eachKeyWord in keywords_dict[eachAttr][eachType] and (eachType == "Strong_Adv" or eachType == "Somewhat_Adv" or eachType == "Neg_Adv"):
                        for each in re.compile(eachKeyWord).findall(buffer_sentence):
                            eachIndex = buffer_sentence.index(each)
                            new_sentence = new_sentence[:buffer_new_sentence.index(each)] + "{" + eachKeyWord + "}" + new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                            buffer_new_sentence = buffer_new_sentence[:buffer_new_sentence.index(each)] + "*"*(len(eachKeyWord)+2) + buffer_new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                            buffer_sentence = buffer_sentence[:eachIndex] + "*"*len(eachKeyWord) + buffer_sentence[eachIndex+len(eachKeyWord):]
                            words_list.append(each)
                            words_index.append(eachIndex)
                            if eachType == "Strong_Adv":
                                words_type.append("Strong_Adv")
                            elif eachType == "Somewhat_Adv":
                                words_type.append("Somewhat_Adv")
                            elif eachType == "Neg_Adv":
                                words_type.append("Neg_Adv")
                            else:
                                pass
                        adv_counter = adv_counter + len(new_word)
                    elif eachKeyWord in keywords_dict[eachAttr][eachType] and eachType == "Conj":
                        for each in re.compile(eachKeyWord).findall(buffer_sentence):
                            eachIndex = buffer_sentence.index(each)
                            new_sentence = new_sentence[:buffer_new_sentence.index(each)] + "$" + eachKeyWord + "$" + new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                            buffer_new_sentence = buffer_new_sentence[:buffer_new_sentence.index(each)] + "*"*(len(eachKeyWord)+2) + buffer_new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                            buffer_sentence = buffer_sentence[:eachIndex] + "*"*len(eachKeyWord) + buffer_sentence[eachIndex+len(eachKeyWord):]
                            words_list.append(each)
                            words_index.append(eachIndex)
                            words_type.append("Conj")
                        conj_counter = conj_counter + len(new_word)        
                    else:
                        pass
    
    "Sort words list, words type"
    for i in range(len(words_index)-1, 0, -1):
        for j in range(i):
            if words_index[j] > words_index[j+1]:
                words_index[j], words_index[j+1] = words_index[j+1], words_index[j]
                words_list[j], words_list[j+1] = words_list[j+1], words_list[j]
                words_type[j], words_type[j+1] = words_type[j+1], words_type[j]            
    
    "Check double type"
    for i in range(len(words_list)):
        if "Verb" in words_type[i]:
            for eachAttr in keywords_dict.keys():
                for eachType in keywords_dict[eachAttr].keys():
                    if words_list[i] in keywords_dict[eachAttr][eachType] and "_Adj" in eachType:
                        if words_list[i] + "的" in eachSen:
                            if eachType == "Neu_Adj":
                                words_type[i] = "Neu_Adj"
                            elif eachType == "Pos_Adj":
                                words_type[i] = "Pos_Adj"
                            else:
                                words_type[i] = "Neg_Adj"
                            verb_counter = verb_counter - 1
                            adj_counter = adj_counter + 1
                            new_sentence = new_sentence.replace("(" + words_list[i] + ")", "[" + words_list[i] + "]")
                        elif words_list[i] == eachSen[len(eachSen)-len(words_list[i]):]:
                            if eachType == "Neu_Adj":
                                words_type[i] = "Neu_Adj"
                            elif eachType == "Pos_Adj":
                                words_type[i] = "Pos_Adj"
                            else:
                                words_type[i] = "Neg_Adj"
                            verb_counter = verb_counter - 1
                            adj_counter = adj_counter + 1
                            new_sentence = new_sentence.replace("(" + words_list[i] + ")", "[" + words_list[i] + "]")
                        else:
                            pass
                    else:
                        pass
        elif "Adj" in words_type[i]:
            for eachAttr in keywords_dict.keys():
                for eachType in keywords_dict[eachAttr].keys():
                    if words_list[i] in keywords_dict[eachAttr][eachType] and "_Adv" in eachType:
                        if i < len(words_list)-1 and "_Adj" in words_type[i+1]:
                            if (words_list[i] + words_list[i+1] in eachSen) or re.search(words_list[i] + "[^和与跟同及、]" + words_list[i+1], eachSen) is not None:
                                if eachType == "Strong_Adv":
                                    words_type[i] = "Strong_Adv"
                                elif eachType == "Somewhat_Adv":
                                    words_type[i] = "Somewhat_Adv"
                                else:
                                    words_type[i] = "Neg_Adv"
                                adj_counter = adj_counter - 1
                                adv_counter = adv_counter + 1
                                new_sentence = new_sentence.replace("[" + words_list[i] + "]", "{" + words_list[i] + "}")
                            else:
                                pass
        elif "Noun" in words_type[i]:
            for eachAttr in keywords_dict.keys():
                for eachType in keywords_dict[eachAttr].keys():
                    if words_list[i] in keywords_dict[eachAttr][eachType] and "_Adj" in eachType:
                        if i < len(words_list)-1 and "_Noun" in words_type[i+1]:
                            if words_list[i] + "的" + words_list[i+1] in eachSen:
                                words_type[i] = eachType
                                adj_counter = adj_counter + 1
                                noun_counter = noun_counter - 1
                                new_sentence = new_sentence.replace("<" + words_list[i] + ">", "[" + words_list[i] + "]")
                            else:
                                pass
                            
        else:
            pass    
    
    "Simplify pattern type"
    simple_words_type = words_type[:]
    simple_words_list = words_list[:]
    simplified = False
    while simplified == False:
        modified = False
        buffer_words_type = list()
        buffer_words_list = list()
        #buffer_sen = "".join(eachSen)
        i = 0
        while i <= len(simple_words_type) - 1:
            if i <= len(simple_words_type) - 2 and "Noun" in simple_words_type[i] and "Noun" in simple_words_type[i+1]:
                if simple_words_list[i] + simple_words_list[i+1] in eachSen:
                    buffer_words_type.append("Noun")
                    buffer_words_list.append(simple_words_list[i] + simple_words_list[i+1])
                    i = i + 2
                    modified = True
                elif re.search(simple_words_list[i] + "[的|这|那|这样|那样|那么|这么]" + simple_words_list[i+1], eachSen) is not None:
                    buffer_words_type.append("Noun")
                    buffer_words_list.append(re.search(simple_words_list[i] + "[的|这|那|这样|那样|那么|这么]" + simple_words_list[i+1], eachSen).group())
                    i = i + 2
                    modified = True
                else:
                    buffer_words_type.append("Noun")
                    buffer_words_list.append(simple_words_list[i])
                    i = i + 1
            elif i <= len(simple_words_type) - 2 and "Adj" in simple_words_type[i] and "Adj" in simple_words_type[i+1]:
                if simple_words_list[i] + simple_words_list[i+1] in eachSen:
                    buffer_words_type.append("Adj")
                    buffer_words_list.append(simple_words_list[i] + simple_words_list[i+1])
                    i = i + 2
                    modified = True
                elif re.search(simple_words_list[i] + "." + simple_words_list[i+1], eachSen) is not None:
                    buffer_words_type.append("Adj")
                    buffer_words_list.append(re.search(simple_words_list[i] + "." + simple_words_list[i+1], eachSen).group())
                    i = i + 2
                    modified = True
                else:
                    buffer_words_type.append("Adj")
                    buffer_words_list.append(simple_words_list[i])
                    i = i + 1
            elif i <= len(simple_words_type) - 2 and (simple_words_type[i] == "Strong_Adv" or simple_words_type[i] == "Somewhat_Adv" or simple_words_type[i] == "Adv") and (simple_words_type[i+1] == "Strong_Adv" or simple_words_type[i+1] == "Somewhat_Adv" or simple_words_type[i+1] == "Adv"):
                if simple_words_list[i] + simple_words_list[i+1] in eachSen:
                    buffer_words_type.append("Adv")
                    buffer_words_list.append(simple_words_list[i] + simple_words_list[i+1])
                    i = i + 2
                    modified = True
                elif re.search(simple_words_list[i] + "." + simple_words_list[i+1], eachSen) is not None:
                    buffer_words_type.append("Adv")
                    buffer_words_list.append(re.search(simple_words_list[i] + "." + simple_words_list[i+1], eachSen).group())
                    i = i + 2
                    modified = True
                else:
                    buffer_words_type.append("Adv")
                    buffer_words_list.append(simple_words_list[i])
                    i = i + 1
            else:
                if "Neg_Adv" in simple_words_type[i]:
                    buffer_words_type.append("Special")
                    buffer_words_list.append(simple_words_list[i])
                    i = i + 1
                elif "Adv" in simple_words_type[i]:
                    buffer_words_type.append("Adv")
                    buffer_words_list.append(simple_words_list[i])
                    i = i + 1
                elif "Special" in simple_words_type[i]:
                    buffer_words_type.append("Special")
                    buffer_words_list.append(simple_words_list[i])
                    i = i + 1
                elif "Adj" in simple_words_type[i]:
                    buffer_words_type.append("Adj")
                    buffer_words_list.append(simple_words_list[i])
                    i = i + 1
                elif "Noun" in simple_words_type[i]:
                    buffer_words_type.append("Noun")
                    buffer_words_list.append(simple_words_list[i])
                    i = i + 1
                elif "Verb" in simple_words_type[i]:
                    buffer_words_type.append("Verb")
                    buffer_words_list.append(simple_words_list[i])
                    i = i + 1
                elif "Conj" in simple_words_type[i]:
                    buffer_words_type.append("Conj")
                    buffer_words_list.append(simple_words_list[i])
                    i = i + 1
                else:
                    pass
        simple_words_type = buffer_words_type[:]
        simple_words_list = buffer_words_list[:]
        if modified == False:
            simplified = True
    
    "Return result"
    sentence_result.append(new_sentence)
    sentence_result.append([noun_counter, adj_counter, adv_counter, verb_counter, conj_counter])
    sentence_result.append(words_list)
    sentence_result.append(words_type)
    sentence_result.append(simple_words_list)
    sentence_result.append(simple_words_type)
    return sentence_result


def isExpectSame(eachSen, simple_words_type, simple_words_list):
    "This function is used to check whether the pattern fulfill is expect same"
    "期待。。。和。。。一样"
    if re.search("希望|期待|期望|想", eachSen) is not None and re.search("和|与|跟|同", eachSen) is not None and re.search("一样|一致|相同", eachSen) is not None:
        pre = re.search("希望|期待|期望|想", eachSen).group()
        middle = re.search("和|与|跟|同", eachSen).group()
        post = re.search("一样|一致|相同", eachSen).group()
        if len(simple_words_list) == 3 and simple_words_type == ["Noun", "Noun", "Adj"]:
            match_string = pre + simple_words_list[0] + middle + simple_words_list[1] + post + ".*?" + simple_words_list[2]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 2 and simple_words_type == ["Noun", "Noun"]:
            match_string = pre + simple_words_list[0] + middle + simple_words_list[1] + post
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 4 and simple_words_type == ["Noun", "Noun", "Adv", "Adj"]:
            match_string = pre + simple_words_list[0] + middle + simple_words_list[1] + post + ".*?" + simple_words_list[2] + ".*?" + simple_words_list[3]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False 
        else:
            return False
    else:
        return False
    

def isAsThanSame(eachSen, simple_words_type, simple_words_list):
    "This function is used to check whether the pattern fulfill as + n + than + n + same"
    "和 。。。比。。。一样"
    if re.search("和|与|跟|同", eachSen) is not None and re.search("比", eachSen) is not None and re.search("一样|相同|没差|差不多|一致", eachSen) is not None:
        pre = re.search("和|与|跟|同", eachSen).group()
        middle = re.search("比", eachSen).group()
        post = re.search("一样|相同|没差|差不多|一致", eachSen).group()
        if len(simple_words_list) == 2 and simple_words_type == ["Noun", "Noun"]:
            match_string = pre + simple_words_list[0] + middle + simple_words_list[1] + post
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 3 and simple_words_type == ["Noun", "Noun", "Adv"]:
            match_string = pre + simple_words_list[0] + middle + simple_words_list[1] + ".*?" + simple_words_list[2] + ".*?" + post
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 3 and simple_words_type == ["Noun", "Noun", "Adj"]:
            match_string = pre + simple_words_list[0] + middle + simple_words_list[1] + post + ".*?" + simple_words_list[2]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 4 and simple_words_type == ["Noun", "Noun", "Adv", "Adj"]:
            match_string = pre + simple_words_list[0] + middle + simple_words_list[1] + ".*?" + simple_words_list[2] + ".*?" + post + ".*?" + simple_words_list[3]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        else:
            return False
    else:
        return False


def isConjunctionAdj(eachSen, simple_words_type, simple_words_list):
    "This function is used to check whether the pattern fulfill n + 及/和/与/同 + n + adj."
    "n + 和  + n "
    if re.search("及|和|与|同|跟", eachSen) is not None:
        and_word = re.search("及|和|与|同|跟", eachSen).group()
        if len(simple_words_list) == 4 and simple_words_type == ["Noun", "Noun", "Adv", "Adj"]:
            match_string = simple_words_list[0] + and_word + simple_words_list[1] + ".*?" + simple_words_list[2] + ".*?" + simple_words_list[3]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 3 and simple_words_type == ["Noun", "Noun", "Adj"]:
            match_string = simple_words_list[0] + and_word + simple_words_list[1] + ".*?" + simple_words_list[2]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        else:
            return False
    else:
        return False


def isExpect(eachSen, simple_words_type, simple_words_list):
    "This function is used to check whether the pattern fulfill expect pattern"
    if re.search("期待|希望|期望|期望", eachSen) is not None:
        word = re.search("期待|希望|期望|期望", eachSen).group()
        if len(simple_words_list) == 3 and simple_words_type == ["Noun", "Adv", "Adj"]:
            match_string = word + simple_words_list[0] + simple_words_list[1] + "一样" + ".*?" + simple_words_list[2]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 2 and simple_words_type == ["Noun", "Adj"]:
            match_string1 = word + simple_words_list[0] + "一样" + ".*?" + simple_words_list[1]
            match_string2 = word + simple_words_list[0] + ".*?" + simple_words_list[1]
            if re.search(match_string1, eachSen) is not None:
                return True
            elif re.search(match_string2, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 1 and simple_words_type == ["Adj"]:
            match_string = word + ".*?" + simple_words_list[0]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 2 and simple_words_type == ["Adv", "Adj"]:
            match_string = word + ".*?" + simple_words_list[0] + simple_words_list[1]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 1 and simple_words_type == ["Noun"]:
            match_string = word + ".*?" + simple_words_list[0]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        else:
            return False
    else:
        return False


def isMoreAndMore(eachSen, simple_words_type, simple_words_list):
    "This function is used to check whether the sentence fulfill more and more"
    "越。。。越。。。"
    if len(re.compile("越").findall(eachSen)) == 2:
        if len(simple_words_list) == 2 and simple_words_type == ["Noun", "Adj"]:
            match_string = "越" + simple_words_list[0] + "越" + simple_words_list[1]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        else:
            return False
    else:
        return False
    
    
def isUnknown(eachSen, simple_words_type, simple_words_list):
    "This function is used to check whether it is a unknown pattern"
    "不知道/不知"
    if re.search("不知道|不知", eachSen) is not None:
        word = re.search("不知道|不知", eachSen).group()
        if len(simple_words_list) == 4 and simple_words_list[1] == simple_words_list[3] and simple_words_type[0] == "Noun" and simple_words_type[1] == "Adj" and simple_words_list[2] == "不":
            match_string = word + ".*?" + simple_words_list[0] + ".*?" + simple_words_list[1] + ".*?" + "不" + ".*?" + simple_words_list[3]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 3 and simple_words_list[0] == simple_words_list[2] and simple_words_type[0] == "Adj" and simple_words_list[1] == "不":
            match_string = word + ".*?" + simple_words_list[0] + ".*?不.*?" + simple_words_list[2]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False 
        elif len(simple_words_list) == 2 and simple_words_type == ["Noun", "Adj"]:
            match_string = word + ".*?" + simple_words_list[0] + ".*?" + simple_words_list[1]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        else:
            return False 
    else:
        return False


def isBothAll(eachSen, simple_words_type, simple_words_list):
    "This function is used to check whether the sentence fulfill both all"
    "n \ n + adj"
    if len(simple_words_list) == 3 and simple_words_type == ["Noun", "Noun", "Adj"]:
        match_string = simple_words_list[0] + "、" + simple_words_list[1] + ".*?" + simple_words_list[2]
        if re.search(match_string, eachSen) is not None:
            return True
        else:
            return False
    elif len(simple_words_list) == 4 and simple_words_type == ["Noun", "Noun", "Adv", "Adj"]:
        match_string = simple_words_list[0] + "、" + simple_words_list[1] + ".*?" + simple_words_list[2] + ".*?" + simple_words_list[3]
        if re.search(match_string, eachSen) is not None:
            return True
        else:
            return False
    else:
        return False


def isSimilar(eachSen, simple_words_type, simple_words_list):
    "This function is used to check whether the pattern fulfill similar pattern"
    if re.search("和|与|跟|同|像", eachSen) is not None and re.search("一样|相同|一致", eachSen) is not None:
        pre = re.search("和|与|跟|同|像", eachSen).group()
        post = re.search("一样|相同|一致", eachSen).group()
        if len(simple_words_list) == 3 and simple_words_type == ["Noun", "Adj", "Adv"]:
            match_string = pre + simple_words_list[0] + ".*?" + post + ".*?" + simple_words_list[1] + ".*?" + simple_words_list[2]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 2 and simple_words_type == ["Noun", "Adj"]:
            match_string = pre + simple_words_list[0] + ".*?" + post + ".*?" + simple_words_list[1]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 1 and simple_words_type == ["Noun"]:
            match_string = pre + simple_words_list[0] + ".*?" + post
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        else:
            return False
    else:
        return False
    
    
def isComparison(eachSen, simple_words_type, simple_words_list):
    "This function is used to test whether the sentence fulfill is Comparsion"
    "比|较"
    if re.search("比|较", eachSen) is not None:
        word = re.search("比|较", eachSen).group()
        if len(simple_words_list) == 3 and simple_words_type == ["Noun", "Noun", "Adj"]:
            match_string = simple_words_list[0] + word + simple_words_list[1] + ".*?" + simple_words_list[2]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 4 and simple_words_type == ["Noun", "Noun", "Adj", "Adv"]:
            match_string = simple_words_list[0] + word + simple_words_list[1] + ".*?" + simple_words_list[2] + ".*?" + simple_words_list[3]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 2 and simple_words_type == ["Noun", "Adj"]:
            match_string = word + simple_words_list[0] + ".*?" + simple_words_list[1]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 3 and simple_words_type == ["Noun", "Adj", "Adv"]:
            match_string = word + simple_words_list[0] + ".*?" + simple_words_list[1] + ".*?" + simple_words_list[2]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        else:
            return False
    else:
        return False
    
    
def isComparison2(eachSen, simple_words_type, simple_words_list):
    "This function is used to check pattern comparison 2"
    "比/较"
    if re.search("于", eachSen) is not None:
        if len(simple_words_list) == 3 and simple_words_type == ["Noun", "Adj" , "Noun"]:
            match_string = simple_words_list[0] + ".*?" + simple_words_list[1] + "于" + simple_words_list[2]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 4 and simple_words_type == ["Noun", "Adv", "Adj", "Noun"]:
            match_string = simple_words_list[0] + ".*?" + simple_words_list[1] + ".*?" + simple_words_list[2] + "于" + simple_words_list[3]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 3 and simple_words_type == ["Adv", "Adj", "Noun"]:
            match_string = simple_words_list[0] + ".*?" + simple_words_list[1] + "于" + simple_words_list[2]
            if re.search(match_string, eachSen) is not None:
                return True
            else:
                return False
        else:
            return False
    else:
        return False


def isNAdj(eachSen, simple_words_type, simple_words_list):
    "This function is used to check whether the sentence is n + adj"
    if len(simple_words_list) == 2 and simple_words_type == ["Noun", "Adj"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1], eachSen) is not None:
            return True
        else:
            return False
    elif len(simple_words_list) == 3 and simple_words_type == ["Noun", "Adj", "Noun"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1] + ".*?" + simple_words_list[2], eachSen) is not None:
            return True
        else:
            return False
    elif len(simple_words_list) == 3 and simple_words_type == ["Noun", "Noun", "Adj"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1] + ".*?" + simple_words_list[2], eachSen) is not None:
            return True
        else:
            return False
    else:
        return False


def isNAdjAdv(eachSen, simple_words_type, simple_words_list):
    "Check n + adj + adv"
    if len(simple_words_list) == 3 and simple_words_type == ["Noun", "Adj", "Adv"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1] + ".*?" + simple_words_list[2], eachSen) is not None:
            return True
        else:
            return False
    elif len(simple_words_list) == 3 and simple_words_type == ["Adv", "Noun", "Adj"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1] + ".*?" + simple_words_list[2], eachSen) is not None:
            return True
        else:
            return False
    else:
        return False


def isNAdvAdj(eachSen, simple_words_type, simple_words_list):
    "Check n + adv + adj"
    if len(simple_words_list) == 3 and simple_words_type == ["Noun", "Adv", "Adj"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1] + ".*?" + simple_words_list[2], eachSen) is not None:
            return True
        else:
            return False
    else:
        return False
    
    
def isAdj(eachSen, simple_words_type, simple_words_list):
    "Check adj"
    if len(simple_words_list) == 1 and simple_words_type == ["Adj"]:
        return True
    elif len(simple_words_list) == 2 and simple_words_type == ["Adv", "Adj"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1], eachSen) is not None:
            return True
        else:
            return False
    else:
        return False
    
    
def isAdjN(eachSen, simple_words_type, simple_words_list):
    "Check Adj"
    if len(simple_words_list) == 2 and simple_words_type == ["Adj", "Noun"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1], eachSen) is not None:
            return True
        else:
            return False
    elif len(simple_words_list) == 3 and simple_words_type == ["Adv", "Adj", "Noun"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1] + ".*?" + simple_words_list[2], eachSen) is not None:
            return True
        else:
            return False
    else:
        return False


def isVerbNoun(eachSen, simple_words_type, simple_words_list):
    "Check verb + n"
    if len(simple_words_list) == 2 and simple_words_type == ["Verb", "Noun"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1], eachSen) is not None:
            return True
        else:
            return False
    elif len(simple_words_list) == 2 and simple_words_type == ["Adv", "Verb"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1], eachSen) is not None:
            return True
        else:
            return False
    elif len(simple_words_list) == 2 and simple_words_type == ["Noun", "Verb"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1], eachSen) is not None:
            return True
        else:
            return False
    elif len(simple_words_list) == 3 and simple_words_type == ["Noun", "Adv", "Verb"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1] + ".*?" + simple_words_list[2], eachSen) is not None:
            return True
        else:
            return False
    elif len(simple_words_list) == 3 and simple_words_type == ["Adv", "Verb", "Noun"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1] + ".*?" + simple_words_list[2], eachSen) is not None:
            return True
        else:
            return False
    elif len(simple_words_list) == 1 and simple_words_type == ["Verb"]:
        return True
    else:
        return False


def isNounOnly(eachSen, simple_words_type, simple_words_list):
    "This function is used to check whether the sentence match noun only pattern"
    if len(simple_words_list) == 1 and simple_words_type == ["Noun"]:
        return True
    elif re.search("好处|优点|优势|强处|毛病|问题|劣势|弱点|坏处", eachSen) is not None and re.search("是|在于|在", eachSen) is not None:
        pre = re.search("好处|优点|优势|强处|毛病|问题|劣势|弱点|坏处", eachSen).group()
        post = re.search("是|在于|在", eachSen).group()
        if len(simple_words_list) == 1 and simple_words_type == ["Noun"]:
            if re.search(pre + ".*?" + post + simple_words_list[0], eachSen) is not None:
                return True
            else:
                return False
        elif len(simple_words_list) == 2 and simple_words_type == ["Noun", "Noun"]:
            if re.search(simple_words_list[0] + ".*?" + pre + ".*?" + post + simple_words_list[1], eachSen) is not None:
                return True
            else:
                return False
        else:
            return False
    elif re.search("是|有", eachSen) is not None and len(simple_words_list) == 2 and simple_words_type == ["Noun", "Noun"]:
        word = re.search("是|有", eachSen).group()
        if re.search(simple_words_list[0] + word + simple_words_list[1], eachSen) is not None:
            return True
        else:
            return False
    elif len(simple_words_list) == 2 and simple_words_type == ["Noun", "Noun"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1], eachSen) is not None:
            return True
        else:
            return False
    elif len(simple_words_list) == 2 and simple_words_type == ["Adv", "Noun"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1], eachSen) is not None:
            return True
        else:
            return False
    elif len(simple_words_list) == 3 and simple_words_type == ["Noun", "Adv", "Noun"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1] + ".*?" + simple_words_list[2], eachSen) is not None:
            return True
        else:
            return False
    else:
        return False
    
    
def isAdvAdjAdvAdj(eachSen, simple_words_type, simple_words_list):
    "This function is used to check whether the sentence is adv + adj + adv + adj"
    if len(simple_words_list) == 5 and simple_words_type == ["Noun", "Adv", "Adj", "Adv", "Adj"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1] + ".*?" + simple_words_list[2] + ".*?" + simple_words_list[3] + ".*?" + simple_words_list[4], eachSen) is not None:
            return True
        else:
            return False
    elif len(simple_words_list) == 4 and simple_words_type == ["Adv", "Adj", "Adv", "Adj"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1] + ".*?" + simple_words_list[2] + ".*?" + simple_words_list[3], eachSen) is not None:
            return True
        else:
            return False
    elif len(simple_words_list) == 4 and simple_words_type == ["Noun", "Adj", "Noun", "Adj"]:
        if re.search(simple_words_list[0] + ".*?" + simple_words_list[1] + ".*?" + simple_words_list[2] + ".*?" + simple_words_list[3], eachSen) is not None:
            return True
        else:
            return False
    else:
        return False


def searchNoun(words_list, words_type, phrase):
    "This function is used to search the last word in the phrase"
    for i in range(len(words_list)):
        if "Noun" in words_type[i] and words_list[i] == phrase[len(phrase)-len(words_list[i]):]:
            return words_list[i]
    return None


def searchAdj(words_list, words_type, phrase):
    "This function is used to search the first word in the phrase"
    for i in range(len(words_list)):
        if "Adj" in words_type[i] and words_list[i] == phrase[:len(words_list[i])]:
            return words_list[i]
    return None


def searchAdv(words_list, words_type, phrase):
    "This function is used to search all adv in the phrase"
    adv_list = list()
    for i in range(len(words_list)):
        if "Adv" in words_type[i] and words_list[i] in phrase:
            adv_list.append(words_list[i])
    if len(adv_list) > 0:
        return adv_list
    else:
        return None


def searchAttrType(word, word_type, keywords_dict):
    "This function is used to search the attribute and type of the word"
    attr_type = list()
    for eachAttr in keywords_dict.keys():
        for eachType in keywords_dict[eachAttr].keys():
            if word in keywords_dict[eachAttr][eachType] and word_type in eachType:
                attr_type.append([eachAttr, eachType])
    return attr_type


def searchAdvType(words, keywords_dict):
    "This function is used to search the type of the adv"
    for eachWord in words:
        if eachWord in keywords_dict["Common"]["Strong_Adv"]:
            return ["Common", "Strong_Adv"]
    return ["Common", "Somewhat_Adv"]


def findNearestEffected(index, attr_list):
    "This function is used to find the nearest effected"
    for i in range(index, len(attr_list)):
        if ("Adj" in attr_list[i][1]) or ("Pos_Noun" in attr_list[i][1]) or ("Neg_Noun" in attr_list[i][1]) or ("Verb" in attr_list[i][1]):
            return i
    for i in range(i, -1, -1):
        if ("Adj" in attr_list[i][1]) or ("Pos_Noun" in attr_list[i][1]) or ("Neg_Noun" in attr_list[i][1]) or ("Verb" in attr_list[i][1]):
            return i
    return None
    
    
def FindNearestNounAttr(index, words_type, attr_type):
    "This function is used to find the nearest noun's attribute"
    for i in range(1, max(index + 1, len(words_type)-index)):
        if (index + i) <= len(words_type) - 1 and "Noun" in words_type[index + i]:
            return [index + i, attr_type[index + i]]
        elif (index - i) >= 0 and "Noun" in words_type[index - i]:
            return [index - i, attr_type[index - i]]
    return None 


def FindIntersectAttr(adj_attr, noun_attr):
    "This function is used to find intersect attribute"
    for i in range(len(adj_attr)):
        for j in range(len(noun_attr)):
            if adj_attr[i][0] == noun_attr[j][0]:
                return [adj_attr[i], noun_attr[j]]
            
    new_adj_attr, new_noun_attr = None, None
    for i in range(len(adj_attr)):
        if "Common" in adj_attr[i][0]:
            new_adj_attr = adj_attr[i]
            break
    if new_adj_attr is None:
        new_adj_attr = adj_attr[0]
        
    for i in range(len(noun_attr)):
        if "总体" in noun_attr[i][0]:
            new_noun_attr = noun_attr[i]
            break
    if new_noun_attr is None:
        new_noun_attr = noun_attr[0]
        
    return [new_adj_attr, new_noun_attr]


def handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type):
    "This function is used to handle words type"
    "Step 1: Find noun attributes"
    "Step 2: Find adv attributes"
    "Step 3: Find adj attributes"
    "Step 4: Find neg adv and change attributes"
    attr_type = [None]*len(simple_words_list)
    '''
    for i in range(len(simple_words_list)):
        if "Noun" in simple_words_type[i]:
            noun = searchNoun(words_list, words_type, simple_words_list[i])
            if noun is not None:
                noun_attr = searchAttrType(noun, "Noun", keywords_dict)[0]
                noun_attr_list.append(noun_attr[0])
                attr_type[i] = noun_attr
    '''
    for i in range(len(simple_words_list)):
        if "Noun" in simple_words_type[i]:
            noun = searchNoun(words_list, words_type, simple_words_list[i])
            if noun is not None:
                noun_attr = searchAttrType(noun, "Noun", keywords_dict)
                if len(noun_attr) == 1:
                    noun_attr = noun_attr[0]
                attr_type[i] = noun_attr
        elif "Adj" in simple_words_type[i]:
            adj = searchAdj(words_list, words_type, simple_words_list[i])
            if adj is not None:
                adj_attr = searchAttrType(adj, "Adj", keywords_dict)
                if len(adj_attr) == 1:
                    adj_attr = adj_attr[0]
                attr_type[i] = adj_attr
        elif "Adv" in simple_words_type[i]:
            adv = searchAdv(words_list, words_type, simple_words_list[i])
            if adv is not None:
                adv_attr = searchAdvType(adv, keywords_dict)
                attr_type[i] = adv_attr
        elif "Verb" in simple_words_type[i]:
            attr_type[i] = searchAttrType(simple_words_list[i], "Verb", keywords_dict)[0]
        elif "Special" in simple_words_type[i]:
            attr_type[i] = ["Special", "Neg_Adv"]
        elif "Conj" in simple_words_type[i]:
            attr_type[i] = ["Common", "Conj"]
        else:
            pass
    
    "Match adj and noun type"
    for i in range(len(simple_words_list)):
        if "Adj" in simple_words_type[i]:
            adj_attr = attr_type[i]
            nearest_noun = FindNearestNounAttr(i, simple_words_type, attr_type)
            '''
            if nearest_noun is not None:
                noun_index = nearest_noun[0]
                noun_attr = nearest_noun[1]
            '''
            if adj_attr != None and nearest_noun != None:
                noun_index = nearest_noun[0]
                noun_attr = nearest_noun[1]
                if type(adj_attr[0]) == type("") and type(noun_attr[0]) == type(""):
                    pass
                elif type(adj_attr[0]) == type("") and type(noun_attr[0]) == type(list()):
                    new_attr = FindIntersectAttr([adj_attr], noun_attr)
                    attr_type[i] = new_attr[0]
                    attr_type[noun_index] = new_attr[1]
                elif type(adj_attr[0]) == type(list()) and type(noun_attr[0]) == type(""):
                    new_attr = FindIntersectAttr(adj_attr, [noun_attr])
                    attr_type[i] = new_attr[0]
                    attr_type[noun_index] = new_attr[1]
                elif type(adj_attr[0]) == type(list()) and type(adj_attr[0]) == type(list()):
                    new_attr = FindIntersectAttr(adj_attr, noun_attr)
                    attr_type[i] = new_attr[0]
                    attr_type[noun_index] = new_attr[1]
                else:
                    pass
            elif adj_attr != None and nearest_noun == None:
                if type(adj_attr[0]) == type(list()):
                    #attr_type[i] = adj_attr[0]
                    found = False
                    for j in range(len(adj_attr)):
                        if "Common" in adj_attr[j][0]:
                            attr_type[i] = adj_attr[j]
                            found = True
                            break 
                    if found == False:
                        attr_type[i] = adj_attr[0]
    
    "Search each in attr_type"
    for i in range(len(attr_type)):
        if type(attr_type[i][0]) == type(list()):
            found = False
            #attr_type[i] = attr_type[i][0]
            for j in range(len(attr_type[i])):
                if "Common" in attr_type[i][j][0] or "总体" in attr_type[i][j][0]:
                    attr_type[i] = attr_type[i][j]
                    found = True
                    break
            if found == False:
                attr_type[i] = attr_type[i][0]
                        
    
    for i in range(len(attr_type)):
        if attr_type[i] == ["Special", "Neg_Adv"]:
            effected_index = findNearestEffected(i, attr_type)
            if effected_index is not None:
                if attr_type[effected_index][1] == "Pos_Noun":
                    attr_type[effected_index][1] = "Neg_Noun"
                elif attr_type[effected_index][1] == "Neg_Noun":
                    attr_type[effected_index][1] = "Pos_Noun"
                elif attr_type[effected_index][1] == "Pos_Verb":
                    attr_type[effected_index][1] = "Neg_Verb"
                elif attr_type[effected_index][1] == "Neg_Verb":
                    attr_type[effected_index][1] = "Pos_Verb"
                elif attr_type[effected_index][1] == "Pos_Adj":
                    attr_type[effected_index][1] = "Neg_Adj"
                elif attr_type[effected_index][1] == "Neg_Adj":
                    attr_type[effected_index][1] = "Pos_Adj"
                elif attr_type[effected_index][1] == "Neu_Adj":
                    attr_type[effected_index][1] = "Pos_Adj"
                else:
                    pass
        
    new_attr_type = list()
    for each in attr_type:
        if each != ["Special", "Neg_Adv"]:
            new_attr_type.append(each)
    
    return new_attr_type
            
            
def ExpectSameGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade pattern: 期待  n 和  n一样好"
    attr_score = dict()
    if sen_words_type == ["Noun", "Noun"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        for each in attr_type:
            attr_score[each[0] + "_Mentioned"] = 1
        noun1 = attr_type[0]
        attr_score["Improvement"] = noun1[0]
    elif sen_words_type == ["Noun", "Noun", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        adj = attr_type[2]
        if noun2[0][-2:] == "总体" and adj[0] != "Common":
            if adj[1] == "Pos_Adj":
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            elif adj[1] == "Neg_Adj":
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            elif adj[1] == "Neu_Adj":
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Pos_Adj":
            attr_score[noun2[0] + "_Score"] = 4
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj":
            attr_score[noun2[0] + "_Score"] = 2
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            attr_score[noun2[0] + "_Score"] = 3
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        else:
            pass
        attr_score["Improvement"] = noun1[0]
    elif sen_words_type == ["Noun", "Noun", "Adv", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        adv = attr_type[2]
        adj = attr_type[3]
        if noun2[0][-2:] == "总体" and adj[0] != "Common":
            if adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
                attr_score[adj[0] + "_Score"] = 5
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
                attr_score[adj[0] + "_Score"] = 1
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            elif adj[1] == "Neu_Adj":
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                pass
        elif adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
            attr_score[noun2[0] + "_Score"] = 5
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
            attr_score[noun2[0] + "_Score"] = 4
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
            attr_score[noun2[0] + "_Score"] = 1
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
            attr_score[noun2[0] + "_Score"] = 2
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            attr_score[noun2[0] + "_Score"] = 3
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        attr_score["Improvement"] = noun1[0]
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None
    

def AsThanSameGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade 和 n 比 n 一样"
    attr_score = dict()
    if sen_words_type == ["Noun", "Noun"] or sen_words_type == ["Noun", "Noun", "Adv"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        attr_score["Comparison"] = noun1[0] + " = " + noun2[0] 
    elif sen_words_type == ["Noun", "Noun", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        adj = attr_type[2]
        if adj[1] == "Pos_Adj":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 4
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 4
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 2
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 2
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 3
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 3
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        attr_score["Comparison"] = noun1[0] + " = " + noun2[0]
    elif sen_words_type == ["Noun", "Noun", "Adv", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        adv = attr_type[2]
        adj = attr_type[3]
        if adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 5
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 5
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 5
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 5
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 4
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 4
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 1
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 1
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 1
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 1
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 2
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 2
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 3
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 3
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        attr_score["Comparison"] = noun1[0] + " = " + noun2[0]
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None


def ConjunctionAdjGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade pattern: n 和  n ... adj"
    attr_score = dict()
    if sen_words_type == ["Noun", "Noun", "Adv", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        adv = attr_type[2]
        adj = attr_type[3]
        if adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 5
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 5
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 5
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 5
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 4
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 4
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 1
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 1
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 1
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 1
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 2
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 2
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 3
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 3
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
    elif sen_words_type == ["Noun", "Noun", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        adj = attr_type[2]
        if adj[1] == "Pos_Adj":
            '''
            attr_score[noun1[0] + "_Score"] = 4
            attr_score[noun2[0] + "_Score"] = 4
            attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            '''
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 4
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 4
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj":
            '''
            attr_score[noun1[0] + "_Score"] = 2
            attr_score[noun2[0] + "_Score"] = 2
            attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            '''
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 2
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 2
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            '''
            attr_score[noun1[0] + "_Score"] = 3
            attr_score[noun2[0] + "_Score"] = 3
            attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            '''
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 3
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 3
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None
    
    
def ExpectGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grading 期待"
    #print (eachSen)
    attr_score = dict()
    if sen_words_type == ["Noun", "Adv", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        attr_score["Improvement"] = noun[0]
    elif sen_words_type == ["Noun", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        attr_score["Improvement"] = noun[0]
    elif sen_words_type == ["Noun"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        attr_score["Improvement"] = noun[0]
    elif sen_words_type == ["Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        adj = attr_type[0]
        if adj[1] != "Common":
            attr_score[adj[1] + "_Mentioned"] = 1
            attr_score["Improvement"] = adj[0]
        else:
            attr_score["总体_Mentioned"] = 1
            attr_score["Improvement"] = "总体"
    elif sen_words_type == ["Adv", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        adj = attr_type[1]
        if adj[0] != "Common":
            attr_score[adj[0] + "_Mentioned"] = 1
            attr_score["Improvement"] = adj[0]
        else:
            attr_score["总体_Mentioned"] = 1
            attr_score["Improvement"] = "总体"
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None


def MoreAndMoreGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade pattern 越 越"
    attr_score = dict()
    if sen_words_type == ["Noun", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        adj = attr_type[1]
        if adj[1] == "Pos_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 4
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 2
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 3
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None


def UnknownGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade pattern 不知道"
    attr_score = dict()
    if sen_words_type == ["Noun", "Adj", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        attr_score[noun[0] + "_Score"] = 99
    elif sen_words_type == ["Adj", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        adj = attr_type[0]
        if adj[0] != "Common":
            attr_score[adj[0] + "_Mentioned"] = 1
            attr_score[adj[0] + "_Score"] = 99
        else:
            attr_score["总体_Mentioned"] = 1
            attr_score["总体_Score"] = 99
    elif sen_words_type == ["Noun", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        attr_score[noun[0] + "_Score"] = 99
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, None]
    else:
        return None


def BothAllGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade pattern 、"
    attr_score = dict()
    if sen_words_type == ["Noun", "Noun", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        adj = attr_type[2]
        if adj[1] == "Pos_Adj":
            '''
            attr_score[noun1[0] + "_Score"] = 4
            attr_score[noun2[0] + "_Score"] = 4
            attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            '''
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 4
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 4
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj":
            '''
            attr_score[noun1[0] + "_Score"] = 2
            attr_score[noun2[0] + "_Score"] = 2
            attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            '''
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 2
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 2
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            '''
            attr_score[noun1[0] + "_Score"] = 3
            attr_score[noun2[0] + "_Score"] = 3
            attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            '''
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 3
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 3
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    elif sen_words_type == ["Noun", "Noun", "Adv", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        adv = attr_type[2]
        adj = attr_type[3]
        if adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
            '''
            attr_score[noun1[0] + "_Score"] = 5
            attr_score[noun2[0] + "_Score"] = 5
            attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            '''
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 5
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 5
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 5
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 5
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
            '''
            attr_score[noun1[0] + "_Score"] = 4
            attr_score[noun2[0] + "_Score"] = 4
            attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            '''
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 4
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 4
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
            '''
            attr_score[noun1[0] + "_Score"] = 1
            attr_score[noun2[0] + "_Score"] = 1
            attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            '''
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 1
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 1
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 1
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 1
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
            '''
            attr_score[noun1[0] + "_Score"] = 2
            attr_score[noun2[0] + "_Score"] = 2
            attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            '''
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 2
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 2
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            '''
            attr_score[noun1[0] + "_Score"] = 3
            attr_score[noun2[0] + "_Score"] = 3
            attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            '''
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun1[0] + "_Score"] = 3
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 3
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None


def SimilarGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade pattern 和 一样"
    attr_score = dict()
    if sen_words_type == ["Noun", "Adj", "Adv"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        adj = attr_type[1]
        adv = attr_type[2]
        if adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 5
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 5
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 4
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 1
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 1
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 2
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 3
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    elif sen_words_type == ["Noun", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        adj = attr_type[1]
        if adj[1] == "Pos_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 4
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 2
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 3
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    elif sen_words_type == ["Noun"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        if noun[1] == "Pos_Noun":
            attr_score[noun[0] + "_Score"] = 4
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif noun[1] == "Neg_Noun":
            attr_score[noun[0] + "_Score"] = 2
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None


def ComparisonGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade pattern 比较"
    attr_score = dict()
    if sen_words_type == ["Noun", "Noun", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        adj = attr_type[2]
        if adj[1] == "Pos_Adj":
            attr_score["Comparison"] = noun1[0] + " > " + noun2[0]
        elif adj[1] == "Neg_Adj":
            attr_score["Comparison"] = noun2[0] + " > " + noun1[0]
        else:
            pass
        if adj[1] == "Pos_Adj":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = simple_words_list[0] + simple_words_list[2]
            else:
                attr_score[noun1[0] + "_Score"] = 4
                attr_score[noun1[0] + "_Reason"] = simple_words_list[0] + simple_words_list[2]
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = simple_words_list[1] + simple_words_list[2]
            else:
                attr_score[noun2[0] + "_Score"] = 2
                attr_score[noun2[0] + "_Reason"] = simple_words_list[1] + simple_words_list[2]
        elif adj[1] == "Neg_Adj":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = simple_words_list[0] + simple_words_list[2]
            else:
                attr_score[noun1[0] + "_Score"] = 2
                attr_score[noun1[0] + "_Reason"] = simple_words_list[0] + simple_words_list[2]
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = simple_words_list[1] + simple_words_list[2]
            else:
                attr_score[noun2[0] + "_Score"] = 4
                attr_score[noun2[0] + "_Reason"] = simple_words_list[1] + simple_words_list[2]
        else:
            pass
    elif sen_words_type == ["Noun", "Noun", "Adj", "Adv"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        adj = attr_type[2]
        adv = attr_type[3]
        if adj[1] == "Pos_Adj":
            attr_score["Comparison"] = noun1[0] + " > " + noun2[0]
        elif adj[1] == "Neg_Adj":
            attr_score["Comparison"] = noun2[0] + " > " + noun1[0]
        else:
            pass
        
        if adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 5
                attr_score[adj[0] + "_Reason"] = simple_words_list[0] + simple_words_list[2]
            else:
                attr_score[noun1[0] + "_Score"] = 5
                attr_score[noun1[0] + "_Reason"] = simple_words_list[0] + simple_words_list[2]
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = simple_words_list[1] + simple_words_list[2]
            else:
                attr_score[noun2[0] + "_Score"] = 2
                attr_score[noun2[0] + "_Reason"] = simple_words_list[1] + simple_words_list[2]
        elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = simple_words_list[0] + simple_words_list[2]
            else:
                attr_score[noun1[0] + "_Score"] = 4
                attr_score[noun1[0] + "_Reason"] = simple_words_list[0] + simple_words_list[2]
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = simple_words_list[1] + simple_words_list[2]
            else:
                attr_score[noun2[0] + "_Score"] = 2
                attr_score[noun2[0] + "_Reason"] = simple_words_list[1] + simple_words_list[2]
        elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 1
                attr_score[adj[0] + "_Reason"] = simple_words_list[0] + simple_words_list[2]
            else:
                attr_score[noun1[0] + "_Score"] = 1
                attr_score[noun1[0] + "_Reason"] = simple_words_list[0] + simple_words_list[2]
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = simple_words_list[1] + simple_words_list[2]
            else:
                attr_score[noun2[0] + "_Score"] = 4
                attr_score[noun2[0] + "_Reason"] = simple_words_list[1] + simple_words_list[2]
        elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
            if noun1[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = simple_words_list[0] + simple_words_list[2]
            else:
                attr_score[noun1[0] + "_Score"] = 2
                attr_score[noun1[0] + "_Reason"] = simple_words_list[0] + simple_words_list[2]
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = simple_words_list[1] + simple_words_list[2]
            else:
                attr_score[noun2[0] + "_Score"] = 4
                attr_score[noun2[0] + "_Reason"] = simple_words_list[1] + simple_words_list[2]
        else:
            pass   
            
    elif sen_words_type == ["Noun", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        adj = attr_type[1]
        
        if adj[1] == "Pos_Adj":
            if adj[0] != "Common":
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = adj[0] + simple_words_list[1]
            else:
                attr_score["总体_Mentioned"] = 1
                attr_score["总体_Score"] = 4
                attr_score["总体_Reason"] = "总体" + simple_words_list[1]
            attr_score[noun[0] + "_Score"] = 2
            attr_score[noun[0] + "_Reason"] = "".join(simple_words_list)
        elif adj[1] == "Neg_Adj":
            if adj[0] != "Common":
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = adj[0] + simple_words_list[1]
            else:
                attr_score["总体_Mentioned"] = 1
                attr_score["总体_Score"] = 2
                attr_score["总体_Reason"] = "总体" + simple_words_list[1]
            attr_score[noun[0] + "_Score"] = 4
            attr_score[noun[0] + "_Reason"] = "".join(simple_words_list)
        else:
            pass
            
    elif sen_words_type == ["Noun", "Adj", "Adv"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        adj = attr_type[1]
        adv = attr_type[2]
        if adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
            if adj[0] != "Common":
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 5
                attr_score[adj[0] + "_Reason"] = adj[0] + simple_words_list[1]
            else:
                attr_score["总体_Mentioned"] = 1
                attr_score["总体_Score"] = 5
                attr_score["总体_Reason"] = "总体" + simple_words_list[1]
            attr_score[noun[0] + "_Score"] = 2
            attr_score[noun[0] + "_Reason"] = "".join(simple_words_list)
        elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
            if adj[0] != "Common":
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = adj[0] + simple_words_list[1]
            else:
                attr_score["总体_Mentioned"] = 1
                attr_score["总体_Score"] = 4
                attr_score["总体_Reason"] = "总体" + simple_words_list[1]
            attr_score[noun[0] + "_Score"] = 2
            attr_score[noun[0] + "_Reason"] = "".join(simple_words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
            if adj[0] != "Common":
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 1
                attr_score[adj[0] + "_Reason"] = adj[0] + simple_words_list[1]
            else:
                attr_score["总体_Mentioned"] = 1
                attr_score["总体_Score"] = 1
                attr_score["总体_Reason"] = "总体" + simple_words_list[1]
            attr_score[noun[0] + "_Score"] = 4
            attr_score[noun[0] + "_Reason"] = "".join(simple_words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
            if adj[0] != "Common":
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = adj[0] + simple_words_list[1]
            else:
                attr_score["总体_Mentioned"] = 1
                attr_score["总体_Score"] = 2
                attr_score["总体_Reason"] = "总体" + simple_words_list[1]
            attr_score[noun[0] + "_Score"] = 4
            attr_score[noun[0] + "_Reason"] = "".join(simple_words_list)
        else:
            pass
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None


def Comparison2Grading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade pattern 于比较"
    attr_score = dict()
    if sen_words_type == ["Noun", "Adj", "Noun"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[2]
        attr_score[noun2[0] + "_Mentioned"] = 1
        adj = attr_type[1]
        if adj[1] == "Pos_Adj":
            attr_score["Comparison"] = noun1[0] + " > " + noun2[0]
        elif adj[1] == "Neg_Adj":
            attr_score["Comparison"] = noun2[0] + " > " + noun1[0]
        else:
            pass
    elif sen_words_type == ["Noun", "Adv", "Adj", "Noun"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[3]
        attr_score[noun2[0] + "_Mentioned"] = 1
        adj = attr_type[1]
        if adj[1] == "Pos_Adj":
            attr_score["Comparison"] = noun1[0] + " > " + noun2[0]
        elif adj[1] == "Neg_Adj":
            attr_score["Comparison"] = noun2[0] + " > " + noun1[0]
        else:
            pass
    elif sen_words_type == ["Adv", "Adj", "Noun"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[2]
        attr_score[noun[0] + "_Mentioned"] = 1
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None


def NAdjGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used tp grade pattern n adj"
    attr_score = dict()
    if sen_words_type == ["Noun", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        adj = attr_type[1]
        if adj[1] == "Pos_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 4
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 2
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 3
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    elif sen_words_type == ["Noun", "Adj", "Noun"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        adj = attr_type[1]
        noun2 = attr_type[2]
        '''
        attr_score[noun1[0] + "_Mentioned"] = 1
        attr_score[noun2[0] + "_Mentioned"] = 1
        '''
        if sen_words_list[1] + "的" + sen_words_list[2] not in eachSen:
            "Describe noun1"
            noun1_attrs = searchAttrType(searchNoun(words_list, words_type, sen_words_list[0]), "Noun", keywords_dict)
            adj_attrs = searchAttrType(searchAdj(words_list, words_type, sen_words_list[1]), "Adj", keywords_dict)
            new_attrs = FindIntersectAttr(adj_attrs, noun1_attrs)
            adj = new_attrs[0]
            noun1 = new_attrs[1]
            attr_score[noun1[0] + "_Mentioned"] = 1
            attr_score[noun2[0] + "_Mentioned"] = 1
            if adj[1] == "Pos_Adj":
                if noun1[0][-2:] == "总体" and adj[0] != "Common":
                    attr_score[noun1[0] + "_Mentioned"] = 0
                    attr_score[adj[0] + "_Mentioned"] = 1
                    attr_score[adj[0] + "_Score"] = 4
                    attr_score[adj[0] + "_Reason"] = "".join(words_list)
                else:
                    attr_score[noun1[0] + "_Score"] = 4
                    attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            elif adj[1] == "Neg_Adj":
                if noun1[0][-2:] == "总体" and adj[0] != "Common":
                    attr_score[noun1[0] + "_Mentioned"] = 0
                    attr_score[adj[0] + "_Mentioned"] = 1
                    attr_score[adj[0] + "_Score"] = 2
                    attr_score[adj[0] + "_Reason"] = "".join(words_list)
                else:
                    attr_score[noun1[0] + "_Score"] = 2
                    attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            elif adj[1] == "Neu_Adj":
                if noun1[0][-2:] == "总体" and adj[0] != "Common":
                    attr_score[noun1[0] + "_Mentioned"] = 0
                    attr_score[adj[0] + "_Mentioned"] = 1
                    attr_score[adj[0] + "_Score"] = 3
                    attr_score[adj[0] + "_Reason"] = "".join(words_list)
                else:
                    attr_score[noun1[0] + "_Score"] = 3
                    attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            else:
                pass
        else:
            "Describe noun2"
            noun2_attrs = searchAttrType(searchNoun(words_list, words_type, sen_words_list[2]), "Noun", keywords_dict)
            adj_attrs = searchAttrType(searchAdj(words_list, words_type, sen_words_list[1]), "Adj", keywords_dict)
            new_attrs = FindIntersectAttr(adj_attrs, noun2_attrs)
            adj = new_attrs[0]
            noun2 = new_attrs[1]
            attr_score[noun1[0] + "_Mentioned"] = 1
            attr_score[noun2[0] + "_Mentioned"] = 1
            if adj[1] == "Pos_Adj":
                if noun2[0][-2:] == "总体" and adj[0] != "Common":
                    attr_score[noun2[0] + "_Mentioned"] = 0
                    attr_score[adj[0] + "_Mentioned"] = 1
                    attr_score[adj[0] + "_Score"] = 4
                    attr_score[adj[0] + "_Reason"] = "".join(words_list)
                else:
                    attr_score[noun2[0] + "_Score"] = 4
                    attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            elif adj[1] == "Neg_Adj":
                if noun2[0][-2:] == "总体" and adj[0] != "Common":
                    attr_score[noun2[0] + "_Mentioned"] = 0
                    attr_score[adj[0] + "_Mentioned"] = 1
                    attr_score[adj[0] + "_Score"] = 2
                    attr_score[adj[0] + "_Reason"] = "".join(words_list)
                else:
                    attr_score[noun2[0] + "_Score"] = 2
                    attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            elif adj[1] == "Neu_Adj":
                if noun2[0][-2:] == "总体" and adj[0] != "Common":
                    attr_score[noun2[0] + "_Mentioned"] = 0
                    attr_score[adj[0] + "_Mentioned"] = 1
                    attr_score[adj[0] + "_Score"] = 3
                    attr_score[adj[0] + "_Reason"] = "".join(words_list)
                else:
                    attr_score[noun2[0] + "_Score"] = 3
                    attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            else:
                pass
    elif sen_words_type == ["Noun", "Noun", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        adj = attr_type[2]
        if adj[1] == "Pos_Adj":
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 4
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj":
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 2
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            if noun2[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun2[0] + "_Score"] = 3
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None


def NAdjAdvGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade pattern n adj adv"
    attr_score = dict()
    if sen_words_type == ["Noun", "Adj", "Adv"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        adj = attr_type[1]
        adv = attr_type[2]
        if adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 5
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 5
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 4
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 1
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 1
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 2
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 3
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    elif sen_words_type == ["Adv", "Noun", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        adv = attr_type[0]
        noun = attr_type[1]
        attr_score[noun[0] + "_Mentioned"] = 1
        adj = attr_type[2]
        if adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 5
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 5
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 4
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 1
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 1
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 2
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 3
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None 
    

def NAdvAdjGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade pattern n adv adj"
    attr_score = dict()
    if sen_words_type == ["Noun", "Adv", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        adv = attr_type[1]
        adj = attr_type[2]
        if adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 5
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 5
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 4
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 1
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 1
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 2
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 3
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None    


def findNearestEffected2(index, words_list, words_type):
    "This function is used to find the nearest affected"
    for i in range(index, len(words_type)):
        if ("Adj" in words_type[i]) or ("Pos_Noun" in words_type[i]) or ("Neg_Noun" in words_type[i]) or ("Verb" in words_type[i]):
            return i
    for i in range(i, -1, -1):
        if ("Adj" in words_type[i]) or ("Pos_Noun" in words_type[i]) or ("Neg_Noun" in words_type[i]) or ("Verb" in words_type[i]):
            return i
    return None


def AdjGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type, last_noun_attr):
    "This function is used to grade pattern adj"
    attr_score = dict()
    new_words_type = words_type[:]
    if sen_words_type == ["Adj"]:
        "Check Neg_Adv"
        for i in range(len(words_list)):
            if "Neg_Adv" in words_type[i]:
                effectedIndex = findNearestEffected2(i, words_list, words_type)
                if effectedIndex is not None:
                    if new_words_type[effectedIndex] == "Pos_Adj":
                        new_words_type[effectedIndex] = "Neg_Adj"
                    elif new_words_type[effectedIndex] == "Neg_Adj":
                        new_words_type[effectedIndex] = "Pos_Adj"
                    elif new_words_type[effectedIndex] == "Neu_Adj":
                        new_words_type[effectedIndex] = "Pos_Adj"
                    else:
                        pass
        for i in range(len(words_list)):
            if "Adj" in words_type[i]:
                adj = searchAttrType(words_list[i], "Adj", keywords_dict)[0]
                adj[1] = new_words_type[i]
                if adj[0] != "Common":
                    attr_score[adj[0] + "_Mentioned"] = 1
                    if adj[1] == "Pos_Adj":
                        attr_score[adj[0] + "_Score"] = 4
                        attr_score[adj[0] + "_Reason"] = "".join(words_list)
                    elif adj[1] == "Neg_Adj":
                        attr_score[adj[0] + "_Score"] = 2
                        attr_score[adj[0] + "_Reason"] = "".join(words_list)
                    elif adj[1] == "Neu_Adj":
                        attr_score[adj[0] + "_Score"] = 3
                        attr_score[adj[0] + "_Reason"] = "".join(words_list)
                    else:
                        pass
                elif adj[0] == "Common" and last_noun_attr is not None:
                    attr_score[last_noun_attr + "_Mentioned"] = 1
                    if adj[1] == "Pos_Adj":
                        attr_score[last_noun_attr + "_Score"] = 4
                        attr_score[last_noun_attr + "_Reason"] = "".join(words_list)
                    elif adj[1] == "Neg_Adj":
                        attr_score[last_noun_attr + "_Score"] = 2
                        attr_score[last_noun_attr + "_Reason"] = "".join(words_list)
                    elif adj[1] == "Neu_Adj":
                        attr_score[last_noun_attr + "_Score"] = 3
                        attr_score[last_noun_attr + "_Reason"] = "".join(words_list)
                    else:
                        pass
                else:
                    attr_score["总体_Mentioned"] = 1
                    if adj[1] == "Pos_Adj":
                        attr_score["总体_Score"] = 4
                        attr_score["总体_Reason"] = "".join(words_list)
                    elif adj[1] == "Neg_Adj":
                        attr_score["总体_Score"] = 2
                        attr_score["总体_Reason"] = "".join(words_list)
                    elif adj[1] == "Neu_Adj":
                        attr_score["总体_Score"] = 3
                        attr_score["总体_Reason"] = "".join(words_list)
                    else:
                        pass
                
    elif sen_words_type == ["Adv", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        adv = attr_type[0]
        "Check Neg_Adv"
        for i in range(len(words_list)):
            if "Neg_Adv" in words_type[i]:
                effectedIndex = findNearestEffected2(i, words_list, words_type)
                if effectedIndex is not None:
                    if new_words_type[effectedIndex] == "Pos_Adj":
                        new_words_type[effectedIndex] = "Neg_Adj"
                    elif new_words_type[effectedIndex] == "Neg_Adj":
                        new_words_type[effectedIndex] = "Pos_Adj"
                    elif new_words_type[effectedIndex] == "Neu_Adj":
                        new_words_type[effectedIndex] = "Pos_Adj"
                    else:
                        pass
        for i in range(len(words_list)):
            if "Adj" in words_type[i]:
                adj = searchAttrType(words_list[i], "Adj", keywords_dict)[0]
                adj[1] = new_words_type[i]
                if adj[0] != "Common":
                    attr_score[adj[0] + "_Mentioned"] = 1
                    if adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
                        attr_score[adj[0] + "_Score"] = 5
                        attr_score[adj[0] + "_Reason"] = "".join(words_list)
                    elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
                        attr_score[adj[0] + "_Score"] = 4
                        attr_score[adj[0] + "_Reason"] = "".join(words_list)
                    elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
                        attr_score[adj[0] + "_Score"] = 1
                        attr_score[adj[0] + "_Reason"] = "".join(words_list)
                    elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
                        attr_score[adj[0] + "_Score"] = 2
                        attr_score[adj[0] + "_Reason"] = "".join(words_list)
                    elif adj[1] == "Neu_Adj":
                        attr_score[adj[0] + "_Score"] = 3
                        attr_score[adj[0] + "_Reason"] = "".join(words_list)
                    else:
                        pass
                elif adj[0] == "Common" and last_noun_attr is not None:
                    attr_score[last_noun_attr + "_Mentioned"] = 1
                    if adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
                        attr_score[last_noun_attr + "_Score"] = 5
                        attr_score[last_noun_attr + "_Reason"] = "".join(words_list)
                    elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
                        attr_score[last_noun_attr + "_Score"] = 4
                        attr_score[last_noun_attr + "_Reason"] = "".join(words_list)
                    elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
                        attr_score[last_noun_attr + "_Score"] = 1
                        attr_score[last_noun_attr + "_Reason"] = "".join(words_list)
                    elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
                        attr_score[last_noun_attr + "_Score"] = 2
                        attr_score[last_noun_attr + "_Reason"] = "".join(words_list)
                    elif adj[1] == "Neu_Adj":
                        attr_score[last_noun_attr + "_Score"] = 3
                        attr_score[last_noun_attr + "_Reason"] = "".join(words_list)
                    else:
                        pass
                else:
                    attr_score["总体_Mentioned"] = 1
                    if adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
                        attr_score["总体_Score"] = 5
                        attr_score["总体_Reason"] = "".join(words_list)
                    elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
                        attr_score["总体_Score"] = 4
                        attr_score["总体_Reason"] = "".join(words_list)
                    elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
                        attr_score["总体_Score"] = 1
                        attr_score["总体_Reason"] = "".join(words_list)
                    elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
                        attr_score["总体_Score"] = 2
                        attr_score["总体_Reason"] = "".join(words_list)
                    elif adj[1] == "Neu_Adj":
                        attr_score["总体_Score"] = 3
                        attr_score["总体_Reason"] = "".join(words_list)
                    else:
                        pass
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, None]
    else:
        return None


def AdjNGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade pattern adj + n"
    attr_score = dict()
    if sen_words_type == ["Adj", "Noun"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        adj = attr_type[0]
        noun = attr_type[1]
        attr_score[noun[0] + "_Mentioned"] = 1
        if adj[1] == "Pos_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 4
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 2
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 3
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    elif sen_words_type == ["Adv", "Adj", "Noun"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        adv = attr_type[0]
        adj = attr_type[1]
        noun = attr_type[2]
        attr_score[noun[0] + "_Mentioned"] = 1
        if adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 5
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 5
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 4
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 1
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 1
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 2
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 3
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass  
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None


def VerbNounGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade v + n"
    attr_score = dict()
    if sen_words_type == ["Verb", "Noun"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        verb = attr_type[0]
        noun = attr_type[1]
        attr_score[noun[0] + "_Mentioned"] = 1
        if verb[1] == "Pos_Verb":
            attr_score[noun[0] + "_Score"] = 4
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif verb[1] == "Neg_Verb":
            attr_score[noun[0] + "_Score"] = 2
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    elif sen_words_type == ["Adv", "Verb"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        adv = attr_type[0]
        verb = attr_type[1]
        if verb[1] == "Pos_Verb" and adv[1] == "Strong_Adv":
            attr_score["总体_Mentioned"] = 1
            attr_score["总体_Score"] = 5
            attr_score["总体_Reason"] = "".join(words_list)
        elif verb[1] == "Pos_Verb" and adv[1] == "Somewhat_Adv":
            attr_score["总体_Mentioned"] = 1
            attr_score["总体_Score"] = 4
            attr_score["总体_Reason"] = "".join(words_list)
        elif verb[1] == "Neg_Verb" and adv[1] == "Strong_Adv":
            attr_score["总体_Mentioned"] = 1
            attr_score["总体_Score"] = 1
            attr_score["总体_Reason"] = "".join(words_list)
        elif verb[1] == "Neg_Verb" and adv[1] == "Somewhat_Adv":
            attr_score["总体_Mentioned"] = 1
            attr_score["总体_Score"] = 2
            attr_score["总体_Reason"] = "".join(words_list)
        else:
            pass
    elif sen_words_type == ["Noun", "Verb"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        verb = attr_type[1]
        if verb[1] == "Pos_Verb":
            attr_score[noun[0] + "_Score"] = 4
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif verb[1] == "Neg_Verb":
            attr_score[noun[0] + "_Score"] = 2
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    elif sen_words_type == ["Noun", "Adv", "Verb"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        adv = attr_type[1]
        verb = attr_type[2]
        if verb[1] == "Pos_Verb" and adv[1] == "Strong_Adv":
            attr_score[noun[0] + "_Score"] = 5
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif verb[1] == "Pos_Verb" and adv[1] == "Somewhat_Adv":
            attr_score[noun[0] + "_Score"] = 4
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif verb[1] == "Neg_Verb" and adv[1] == "Strong_Adv":
            attr_score[noun[0] + "_Score"] = 1
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif verb[1] == "neg_Verb" and adv[1] == "Somewhat_Adv":
            attr_score[noun[0] + "_Score"] = 2
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    elif sen_words_type == ["Adv", "Verb", "Noun"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        adv = attr_type[0]
        verb = attr_type[1]
        noun = attr_type[2]
        attr_score[noun[0] + "_Mentioned"] = 1
        if verb[1] == "Pos_Verb" and adv[1] == "Strong_Adv":
            attr_score[noun[0] + "_Score"] = 5
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif verb[1] == "Pos_Verb" and adv[1] == "Somewhat_Adv":
            attr_score[noun[0] + "_Score"] = 4
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif verb[1] == "Neg_Verb" and adv[1] == "Strong_Adv":
            attr_score[noun[0] + "_Score"] = 1
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif verb[1] == "neg_Verb" and adv[1] == "Somewhat_Adv":
            attr_score[noun[0] + "_Score"] = 2
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    elif sen_words_type == ["Verb"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        verb = attr_type[0]
        attr_score["总体_Mentioned"] = 1
        if verb[1] == "Pos_Verb":
            attr_score["总体_Score"] = 4
            attr_score["总体_Reason"] = "".join(words_list)
        elif verb[1] == "Neg_Verb":
            attr_score["总体_Score"] = 2
            attr_score["总体_Reason"] = "".join(words_list)
        else:
            pass
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None


def NounOnlyGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade pattern n"
    attr_score = dict()
    if sen_words_type == ["Noun"] and re.search("好处|优点|优势|强处", eachSen) is not None and re.search("是|在于|在", eachSen) is not None:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        attr_score[noun[0] + "_Score"] = 4
        attr_score[noun[0] + "_Reason"] = "".join(words_list)
    elif sen_words_type == ["Noun"] and re.search("毛病|问题|劣势|弱点|坏处", eachSen) is not None and re.search("是|在于|在", eachSen) is not None:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        attr_score[noun[0] + "_Score"] = 4
        attr_score[noun[0] + "_Reason"] = "".join(words_list)
    elif sen_words_type == ["Noun"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        if noun[1] == "Pos_Noun":
            attr_score[noun[0] + "_Score"] = 4
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif noun[1] == "Neg_Noun":
            attr_score[noun[0] + "_Score"] = 2
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    elif sen_words_type == ["Noun", "Noun"] and re.search("好处|优点|优势|强处", eachSen) is not None and re.search("是|在于|在", eachSen) is not None:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        attr_score[noun2[0] + "_Score"] = 4
        attr_score[noun2[0] + "_Reason"] = "".join(words_list)
    elif sen_words_type == ["Noun", "Noun"] and re.search("毛病|问题|劣势|弱点|坏处", eachSen) is not None and re.search("是|在于|在", eachSen) is not None:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        attr_score[noun2[0] + "_Score"] = 2
        attr_score[noun2[0] + "_Reason"] = "".join(words_list)
    elif sen_words_type == ["Noun", "Noun"] and re.search("是|有", eachSen) is not None:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        if noun2[0] == "Pos_Noun":
            attr_score[noun2[0] + "_Score"] = 4
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif noun2[0] == "Neg_Noun":
            attr_score[noun2[0] + "_Score"] = 2
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    elif sen_words_type == ["Noun", "Noun"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        if noun1[0] == "Pos_Noun":
            attr_score[noun1[0] + "_Score"] = 4
            attr_score[noun1[0] + "_Reason"] = "".join(words_list)
        elif noun1[0] == "Neg_Noun":
            attr_score[noun1[0] + "_Score"] = 2
            attr_score[noun1[0] + "_Reason"] = "".join(words_list)
        else:
            pass
        noun2 = attr_type[1]
        attr_score[noun2[0] + "_Mentioned"] = 1
        if noun2[0] == "Pos_Noun":
            attr_score[noun2[0] + "_Score"] = 4
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif noun2[0] == "Neg_Noun":
            attr_score[noun2[0] + "_Score"] = 2
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    elif sen_words_type == ["Adv", "Noun"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        adv = attr_type[0]
        noun = attr_type[1]
        attr_score[noun[0] + "_Mentioned"] = 1
        if noun[0] == "Pos_Noun" and adv[0] == "Strong_Adv":
            attr_score[noun[0] + "_Score"] = 5
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif noun[0] == "Pos_Noun" and adv[0] == "Somewhat_Adv":
            attr_score[noun[0] + "_Score"] = 4
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif noun[0] == "Neg_Noun" and adv[0] == "Strong_Adv":
            attr_score[noun[0] + "_Score"] = 1
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif noun[0] == "Neg_Noun" and adv[0] == "Somewhat_Adv":
            attr_score[noun[0] + "_Score"] = 2
            attr_score[noun[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    elif sen_words_type == ["Noun", "Adv", "Noun"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        adv = attr_type[1]
        noun2 = attr_type[2]
        attr_score[noun2[0] + "_Mentioned"] = 1
        if noun2[0] == "Pos_Noun" and adv[0] == "Strong_Adv":
            attr_score[noun2[0] + "_Score"] = 5
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif noun2[0] == "Pos_Noun" and adv[0] == "Somewhat_Adv":
            attr_score[noun2[0] + "_Score"] = 4
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif noun2[0] == "Neg_Noun" and adv[0] == "Strong_Adv":
            attr_score[noun2[0] + "_Score"] = 1
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        elif noun2[0] == "Neg_Noun" and adv[0] == "Somewhat_Adv":
            attr_score[noun2[0] + "_Score"] = 2
            attr_score[noun2[0] + "_Reason"] = "".join(words_list)
        else:
            pass
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None


def AdvAdjAdvAdjGrading(eachSen, keyword_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade pattern adv adj adv adj "
    attr_score = dict()
    if sen_words_type == ["Noun", "Adv", "Adj", "Adv", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun = attr_type[0]
        attr_score[noun[0] + "_Mentioned"] = 1
        adv = attr_type[1]
        adj = attr_type[2]
        if adj[1] == "Pos_Adj" and adv[1] == "Strong_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 5
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 5
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Pos_Adj" and adv[1] == "Somewhat_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 4
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 4
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Strong_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 1
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 1
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neg_Adj" and adv[1] == "Somewhat_Adv":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 2
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 2
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
        elif adj[1] == "Neu_Adj":
            if noun[0][-2:] == "总体" and adj[0] != "Common":
                attr_score[noun[0] + "_Mentioned"] = 0
                attr_score[adj[0] + "_Mentioned"] = 1
                attr_score[adj[0] + "_Score"] = 3
                attr_score[adj[0] + "_Reason"] = "".join(words_list)
            else:
                attr_score[noun[0] + "_Score"] = 3
                attr_score[noun[0] + "_Reason"] = "".join(words_list)
    elif sen_words_type == ["Adv", "Adj", "Adv", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        adv1 = attr_type[0]
        adj1 = attr_type[1]
        if adj1[0] != "Common":
            attr_score[adj1[0] + "_Mentioned"] = 1
            if adj1[1] == "Pos_Adj" and adv1[1] == "Strong_Adv":
                attr_score[adj1[0] + "_Score"] = 5
                attr_score[adj1[0] + "_Reason"] = "".join(words_list)
            elif adj1[1] == "Pos_Adj" and adv1[1] == "Somewhat_Adv":
                attr_score[adj1[0] + "_Score"] = 4
                attr_score[adj1[0] + "_Reason"] = "".join(words_list)
            elif adj1[1] == "Neg_Adj" and adv1[1] == "Strong_Adv":
                attr_score[adj1[0] + "_Score"] = 1 
                attr_score[adj1[0] + "_Reason"] = "".join(words_list)
            elif adj1[1] == "Neg_Adj" and adv1[1] == "Somewhat_Adv":
                attr_score[adj1[0] + "_Score"] = 3 
                attr_score[adj1[0] + "_Reason"] = "".join(words_list)
            elif adj1[1] == "Neu_Adj":
                attr_score[adj1[0] + "_Score"] = 3
                attr_score[adj1[0] + "_Reason"] = "".join(words_list)
            else:
                pass
        else:
            attr_score["总体_Mentioned"] = 1
            if adj1[1] == "Pos_Adj" and adv1[1] == "Strong_Adv":
                attr_score["总体_Score"] = 5
                attr_score["总体_Reason"] = "".join(words_list)
            elif adj1[1] == "Pos_Adj" and adv1[1] == "Somewhat_Adv":
                attr_score["总体_Score"] = 4
                attr_score["总体_Reason"] = "".join(words_list)
            elif adj1[1] == "Neg_Adj" and adv1[1] == "Strong_Adv":
                attr_score["总体_Score"] = 1 
                attr_score["总体_Reason"] = "".join(words_list)
            elif adj1[1] == "Neg_Adj" and adv1[1] == "Somewhat_Adv":
                attr_score["总体_Score"] = 3 
                attr_score["总体_Reason"] = "".join(words_list)
            elif adj1[1] == "Neu_Adj":
                attr_score["总体_Score"] = 3
                attr_score["总体_Reason"] = "".join(words_list)
            else:
                pass
        
        adv2 = attr_type[2]
        adj2 = attr_type[3]
        if adj2[0] != "Common":
            attr_score[adj2[0] + "_Mentioned"] = 1
            if adj2[1] == "Pos_Adj" and adv2[1] == "Strong_Adv":
                attr_score[adj2[0] + "_Score"] = 5
                attr_score[adj2[0] + "_Reason"] = "".join(words_list)
            elif adj2[1] == "Pos_Adj" and adv2[1] == "Somewhat_Adv":
                attr_score[adj2[0] + "_Score"] = 4
                attr_score[adj2[0] + "_Reason"] = "".join(words_list)
            elif adj2[1] == "Neg_Adj" and adv2[1] == "Strong_Adv":
                attr_score[adj2[0] + "_Score"] = 1 
                attr_score[adj2[0] + "_Reason"] = "".join(words_list)
            elif adj2[1] == "Neg_Adj" and adv2[1] == "Somewhat_Adv":
                attr_score[adj2[0] + "_Score"] = 3 
                attr_score[adj2[0] + "_Reason"] = "".join(words_list)
            elif adj2[1] == "Neu_Adj":
                attr_score[adj2[0] + "_Score"] = 3
                attr_score[adj2[0] + "_Reason"] = "".join(words_list)
            else:
                pass
        else:
            attr_score["总体_Mentioned"] = 1
            if adj2[1] == "Pos_Adj" and adv2[1] == "Strong_Adv":
                attr_score["总体_Score"] = 5
                attr_score["总体_Reason"] = "".join(words_list)
            elif adj2[1] == "Pos_Adj" and adv2[1] == "Somewhat_Adv":
                attr_score["总体_Score"] = 4
                attr_score["总体_Reason"] = "".join(words_list)
            elif adj2[1] == "Neg_Adj" and adv2[1] == "Strong_Adv":
                attr_score["总体_Score"] = 1 
                attr_score["总体_Reason"] = "".join(words_list)
            elif adj2[1] == "Neg_Adj" and adv2[1] == "Somewhat_Adv":
                attr_score["总体_Score"] = 3 
                attr_score["总体_Reason"] = "".join(words_list)
            elif adj2[1] == "Neu_Adj":
                attr_score["总体_Score"] = 3
                attr_score["总体_Reason"] = "".join(words_list)
            else:
                pass
    elif sen_words_type == ["Noun", "Adj", "Noun", "Adj"]:
        attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
        noun1 = attr_type[0]
        attr_score[noun1[0] + "_Mentioned"] = 1
        adj1 = attr_type[1]
        noun2 = attr_type[2]
        attr_score[noun2[0] + "_Mentioned"] = 1
        adj2 = attr_type[3]
        if noun1[0][-2:] == "总体" and adj1[0] != "Common":
            if adj1[1] == "Pos_Adj":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj1[0] + "_Mentioned"] = 1
                attr_score[adj1[0] + "_Score"] = 4
                attr_score[adj1[0] + "_Reason"] = "".join(words_list)
            elif adj1[1] == "Neg_Adj":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj1[0] + "_Mentioned"] = 1
                attr_score[adj1[0] + "_Score"] = 2
                attr_score[adj1[0] + "_Reason"] = "".join(words_list)
            elif adj1[1] == "Neu_Adj":
                attr_score[noun1[0] + "_Mentioned"] = 0
                attr_score[adj1[0] + "_Mentioned"] = 1
                attr_score[adj1[0] + "_Score"] = 3
                attr_score[adj1[0] + "_Reason"] = "".join(words_list)
            else:
                pass
        else:
            if adj1[1] == "Pos_Adj":
                attr_score[noun1[0] + "_Score"] = 4
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            elif adj1[1] == "Neg_Adj":
                attr_score[noun1[0] + "_Score"] = 2
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            elif adj1[1] == "Neu_Adj":
                attr_score[noun1[0] + "_Score"] = 3
                attr_score[noun1[0] + "_Reason"] = "".join(words_list)
            else:
                pass
        if noun2[0][-2:] == "总体" and adj2[0] != "Common":
            if adj2[1] == "Pos_Adj":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj2[0] + "_Mentioned"] = 1
                attr_score[adj2[0] + "_Score"] = 4
                attr_score[adj2[0] + "_Reason"] = "".join(words_list)
            elif adj2[1] == "Neg_Adj":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj2[0] + "_Mentioned"] = 1
                attr_score[adj2[0] + "_Score"] = 2
                attr_score[adj2[0] + "_Reason"] = "".join(words_list)
            elif adj2[1] == "Neu_Adj":
                attr_score[noun2[0] + "_Mentioned"] = 0
                attr_score[adj2[0] + "_Mentioned"] = 1
                attr_score[adj2[0] + "_Score"] = 3
                attr_score[adj2[0] + "_Reason"] = "".join(words_list)
            else:
                pass
        else:
            if adj2[1] == "Pos_Adj":
                attr_score[noun2[0] + "_Score"] = 4
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            elif adj2[1] == "Neg_Adj":
                attr_score[noun2[0] + "_Score"] = 2
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            elif adj2[1] == "Neu_Adj":
                attr_score[noun2[0] + "_Score"] = 3
                attr_score[noun2[0] + "_Reason"] = "".join(words_list)
            else:
                pass
    else:
        pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type]
    else:
        return None


def OthersGrading(eachSen, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type):
    "This function is used to grade sentences that are not belong to any pattern"
    attr_score = dict()
    attr_type = handleWordsType(keywords_dict, words_list, words_type, simple_words_list, simple_words_type)
    for i in range(len(attr_type)):
        if "_Noun" in attr_type[i][1] and attr_type[i][0] != "总体":
            attr_score[attr_type[i][0] + "_Mentioned"] = 1
        if "_Adj" in attr_type[i][1]:
            adj_attr = attr_type[i]
            noun_attr = None
            noun_index = None
            '''
            for index in range(1, max(i+1, len(attr_type)-i)):
                if (i + index) <= len(attr_type) - 1 and "Noun" in attr_type[i+index][1]:
                    noun_attr = attr_type[i + index]
                    noun_index = i + index
                    break
                elif (i - index) >= 0 and "Noun" in attr_type[i - index][1]:
                    noun_attr = attr_type[i - index]
                    noun_index = i - index
                    break
                else:
                    pass
            '''
            "Find the noun before then after"
            if i+1 <= len(sen_words_list)-1 and sen_words_list[i] + "的" + sen_words_list[i+1] in eachSen and "Noun" in attr_type[i+1][1]:
                noun_attr = attr_type[i + 1]
                noun_index = i + 1
            if noun_attr is None and noun_index is None:
                for index in range(i)[::-1]:
                    if "Noun" in attr_type[index][1]:
                        noun_attr = attr_type[index]
                        noun_index = index
                        break
            if noun_attr is None and noun_index is None:
                for index in range(i+1, len(attr_score)):
                    if "Noun" in attr_type[index][1]:
                        noun_attr = attr_type[index]
                        noun_index = index
                        break
            
            if noun_attr is not None:
                if noun_attr[0][-2:] == "总体" and adj_attr[0] != "Common":
                    if adj_attr[1] == "Pos_Adj":
                        attr_score[adj_attr[0] + "_Mentioned"] = 1
                        attr_score[adj_attr[0] + "_Score"] = 4
                        attr_score[adj_attr[0] + "_Reason"] = "".join(words_list)
                    elif adj_attr[1] == "Neg_Adj":
                        attr_score[adj_attr[0] + "_Mentioned"] = 1
                        attr_score[adj_attr[0] + "_Score"] = 2
                        attr_score[adj_attr[0] + "_Reason"] = "".join(words_list)
                    elif adj_attr[1] == "Neu_Adj":
                        attr_score[adj_attr[0] + "_Mentioned"] = 1
                        attr_score[adj_attr[0] + "_Score"] = 3
                        attr_score[adj_attr[0] + "_Reason"] = "".join(words_list)
                    else:
                        pass
                else:
                    if adj_attr[1] == "Pos_Adj":
                        attr_score[noun_attr[0] + "_Mentioned"] = 1
                        attr_score[noun_attr[0] + "_Score"] = 4
                        attr_score[noun_attr[0] + "_Reason"] = "".join(words_list)
                    elif adj_attr[1] == "Neg_Adj":
                        attr_score[noun_attr[0] + "_Mentioned"] = 1
                        attr_score[noun_attr[0] + "_Score"] = 2
                        attr_score[noun_attr[0] + "_Reason"] = "".join(words_list)
                    elif adj_attr[1] == "Neu_Adj":
                        attr_score[noun_attr[0] + "_Mentioned"] = 1
                        attr_score[noun_attr[0] + "_Score"] = 3
                        attr_score[noun_attr[0] + "_Reason"] = "".join(words_list)
            else:
                pass
    
    if len(attr_score.keys()) > 0:
        return [attr_score, attr_type, eachSen]
    else:
        return None  
    

def OutputResult(output_file_name, origin_review, attribute_list, review_score, sen_id, eachSen):
    "This function is used to output result"
    #print (review_score["Improvement"])
    graded = False
    for eachAttr in attribute_list:
        if review_score[eachAttr + "_Mentioned"] != 0:
            output_str = origin_review + ";" + str(sen_id) + ";" + eachSen + ";" + eachAttr + ";" + str(review_score[eachAttr + "_Score"]) + ";" + str(review_score[eachAttr + "_Reason"]) + "\r\n"
            output_file = open(output_file_name, "a")
            output_file.write(output_str)
            output_file.close()
            graded = True
        elif review_score[eachAttr + "_Score"] > 0:
            output_str = origin_review + ";" + str(sen_id) + ";" + eachSen + ";" + eachAttr + ";" + str(review_score[eachAttr + "_Score"]) + ";" + str(review_score[eachAttr + "_Reason"]) + "\r\n"
            output_file = open(output_file_name, "a")
            output_file.write(output_str)
            output_file.close()
            graded = True
        else:
            pass
    
    if review_score["Improvement"] != "":
        output_str = origin_review + ";" + str(sen_id) + ";" + eachSen + ";" + str(review_score["Improvement"]) + ";改进" + ";\r\n"
        output_file = open(output_file_name, "a")
        output_file.write(output_str)
        output_file.close()
        graded = True
    
    if review_score["Comparison"] != "":
        output_str = origin_review + ";" + str(sen_id) + ";" + eachSen + ";比较;" + str(review_score["Comparison"]) + ";比较;" + ";\r\n"
        output_file = open(output_file_name, "a")
        output_file.write(output_str)
        output_file.close()
        graded = True
     
    if graded == False:
        output_str = origin_review + ";" + str(sen_id) + ";" + eachSen + ";;;\r\n"
        output_file = open(output_file_name, "a")
        output_file.write(output_str)
        output_file.close()




if __name__ == "__main__": 
    "Main Body"

    "！！！！！！！！！！！！！！！！！Read attributes"
    attribute_list = ReadInAttributes("C:/Users/Administrator/PycharmProjects/untitled/ckcode/keywords/keyword.txt")
    
    "！！！！！！！！！！！！！！Read keywords"
    keywords_dict = ReadInKeyWords("C:/Users/Administrator/PycharmProjects/untitled/ckcode/keywords/keyword.txt")

    keywords_list = list()
    for eachAttr in keywords_dict.keys():
        for eachType in keywords_dict[eachAttr].keys():
            for eachWord in keywords_dict[eachAttr][eachType]:
                if eachWord != "" and eachWord not in keywords_list:
                    keywords_list.append(eachWord)
    keywords_list.sort(key = len, reverse = True)
    
    "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Read Reviews"
    reviews = ReadInReviews("C:\Users\Administrator\PycharmProjects\untitled\ckcode\eviews\Hannah(1).txt")

    
    "Analyze each sentences"
    for eachReview in reviews:
        origin_review = eachReview[0]

        last_noun_attr = None
        sen_id = 1
        
        for eachSentence in eachReview[1]:
            if eachSentence != "":
                "Review Score"
                review_score = dict()
                for eachAttr in attribute_list:
                    review_score[eachAttr + "_Mentioned"] = 0
                    review_score[eachAttr + "_Score"] = 0
                    review_score[eachAttr + "_Sentence"] = ""
                    review_score[eachAttr + "_Reason"] = ""
                review_score["Improvement"] = ""
                review_score["Comparison"] = ""
                
                sentence_result = AnalyzeEachSentence(keywords_dict, keywords_list, eachSentence, "C:\Users\Administrator\PycharmProjects\untitled\ckcode\stopwords\stop words Mar 10 UTF8.txt")
                words_list = sentence_result[2]
                words_type = sentence_result[3]
                simple_words_list = sentence_result[4]
                simple_words_type = sentence_result[5]
                sen_words_list, sen_words_type = list(), list()
                for i in range(len(simple_words_list)):
                    if simple_words_type[i] != "Special":
                        sen_words_list.append(simple_words_list[i])
                        sen_words_type.append(simple_words_type[i])
                   
                "Check sentence pattern"
                if isExpectSame(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = ExpectSameGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isAsThanSame(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = AsThanSameGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isConjunctionAdj(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = ConjunctionAdjGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isExpect(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = ExpectGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isMoreAndMore(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = MoreAndMoreGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isUnknown(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = UnknownGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isBothAll(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = BothAllGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isSimilar(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = SimilarGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isComparison(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = ComparisonGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isComparison2(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = Comparison2Grading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isNAdj(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = NAdjGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isNAdjAdv(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = NAdjAdvGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isNAdvAdj(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = NAdvAdjGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isAdj(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = AdjGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type, last_noun_attr)
                elif isAdjN(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = AdjNGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isVerbNoun(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = VerbNounGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isNounOnly(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = NounOnlyGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                elif isAdvAdjAdvAdj(eachSentence, sen_words_type, sen_words_list) == True:
                    grade = AdvAdjAdvAdjGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)
                else:
                    grade = OthersGrading(eachSentence, keywords_dict, words_list, words_type, simple_words_list, simple_words_type, sen_words_list, sen_words_type)

                "Update Review"   
                if grade is not None and grade[0] is not None:
                    for eachKey in grade[0].keys():

                        if "Mentioned" in eachKey and eachKey in review_score.keys() and review_score[eachKey] < grade[0][eachKey]:
                            review_score[eachKey] = grade[0][eachKey]
                        elif "Score" in eachKey and eachKey in review_score.keys() and review_score[eachKey] < grade[0][eachKey]:
                            attr_score = eachKey.split("_")[0]
                            review_score[eachKey] = grade[0][eachKey]                            
                            if (attr_score + "_Reason") in grade[0].keys() and (attr_score + "_Reason") in review_score.keys():
                                review_score[attr_score + "_Reason"] = grade[0][attr_score + "_Reason"]
                        elif "Improvement" in eachKey:
                            review_score[eachKey] = grade[0][eachKey]
                        elif "Comparison" in eachKey:
                            review_score[eachKey] = grade[0][eachKey]
                        else:
                            pass

                "!!!!!!!!!!!!!!!!!!!!!output result"
                OutputResult("C:\Users\Administrator\PycharmProjects\untitled\ckcode\eviews\esult.txt", origin_review, attribute_list, review_score, sen_id, eachSentence)
                sen_id = sen_id + 1